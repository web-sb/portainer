"""
"""

import logging
import mesos
import os
import progressbar
import StringIO
import tarfile
import tempfile
import threading
import time
import uuid

from fs.osfs import OSFS
from fs.s3fs import S3FS

from Queue import Queue
from urlparse import urlparse
from ddocker.app import subcommand
from ddocker.proto import ddocker_pb2
from ddocker.proto import mesos_pb2
from ddocker.util.parser import parse_dockerfile

logger = logging.getLogger("ddocker.build")


def args(parser):
    parser.add_argument("dockerfile", action="append")

    parser.add_argument("--executor-uri", dest="executor", required=True,
                        help="URI to the ddocker executor for mesos")

    # Isolation
    group = parser.add_argument_group("isolation")
    group.add_argument("--cpu-limit", default=1.0,
                       help="CPU allocated to building the image")
    group.add_argument("--mem-limit", default=256,
                       help="Memory allocated to building the image (mb)")

    # Arguments for the staging filesystem
    group = parser.add_argument_group("fs")
    group.add_argument("--staging-uri", default="/tmp/ddocker",
                       help="The URI to use as a base directory for staging files.")
    group.add_argument("--aws-access-key-id", default=os.environ.get("AWS_ACCESS_KEY_ID"),
                       help="Access key for using the S3 filesystem")
    group.add_argument("--aws-secret-access-key", default=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                       help="Secret key for using the S3 filesystem")


@subcommand("build", callback=args)
def main(args):

    logger.info("Building docker image from %s", args.dockerfile)

    task_queue = Queue()

    # Launch the mesos framework
    framework = mesos_pb2.FrameworkInfo()
    framework.user = "root"
    framework.name = "ddocker"
    framework.failover_timeout = 300  # Timeout after 300 seconds

    # Figure out the framework info from an existing checkpoint
    if args.checkpoint and os.path.exists(args.checkpoint):
        with open(args.checkpoint) as cp:
            checkpoint = ddocker_pb2.Checkpoint()
            ddocker_pb2.Checkpoint.ParseFromString(
                checkpoint, cp.read()
            )

            if not checkpoint.frameworkId:
                raise RuntimeError("No framework ID in the checkpoint")

            logger.info("Registering with checkpoint framework ID %s", checkpoint.frameworkId)
            framework.id.value = checkpoint.frameworkId

    # Create the executor
    executor = mesos_pb2.ExecutorInfo()
    executor.executor_id.value = "builder"
    executor.command.value = "./%s executor" % os.path.basename(args.executor)
    executor.name = "Docker Build Executor"
    executor.source = "ddocker"

    # Configure the mesos executor with the ddocker executor uri
    ddocker_executor = executor.command.uris.add()
    ddocker_executor.value = args.executor
    ddocker_executor.executable = True

    # Kick off the scheduler driver
    scheduler = Scheduler(
        task_queue,
        executor,
        args.checkpoint,
        args.cpu_limit,
        args.mem_limit,
        args
    )
    driver = mesos.MesosSchedulerDriver(
        scheduler, framework, args.mesos_master
    )

    # Put the task onto the queue
    for dockerfile in args.dockerfile:
        task_queue.put(dockerfile)

    thread = threading.Thread(target=driver.run)
    thread.setDaemon(True)
    thread.start()

    # Wait here until the tasks are done
    while thread.isAlive():
        time.sleep(0.5)


def make_build_context(output, context_root, dockerfile):
    """Generate and return a compressed tar archive of the build context."""

    tar = tarfile.open(mode="w:gz", fileobj=output)
    for idx, (cmd, instruction) in enumerate(dockerfile.instructions):
        if cmd == "ADD":
            local_path, remote_path = instruction
            tar_path = "context/%s" % str(idx)

            if not local_path.startswith("/"):
                local_path = os.path.join(context_root, local_path)
            local_path = os.path.abspath(local_path)

            logger.debug("Adding path %s to tar at %s", local_path, tar_path)
            tar.add(local_path, arcname=tar_path)
            dockerfile.instructions[idx] = (cmd, (tar_path, remote_path))

    # Write the modified dockerfile into the tar also
    buildfile = StringIO.StringIO()
    buildfile.write("# Generated by ddocker\n")

    for cmd, instructions in dockerfile.instructions:
        if cmd not in dockerfile.INTERNAL:
            line = "%s %s" % (cmd, " ".join(instructions))

            logger.debug("Added command %r to new dockerfile", line)
            buildfile.write("%s\n" % line)

    buildfile.seek(0, os.SEEK_END)
    info = tarfile.TarInfo("Dockerfile")
    info.size = buildfile.tell()

    buildfile.seek(0)
    tar.addfile(info, fileobj=buildfile)

    tar.close()
    output.seek(0, os.SEEK_END)
    tar_size = output.tell()
    output.seek(0)

    return tar_size


def create_filesystem(staging_uri, s3_key, s3_secret):
    """Create an instance of a filesystem based on the URI"""

    url = urlparse(staging_uri)

    # Local filesystem
    if not url.scheme:
        return OSFS(
            root_path=url.path,
            create=True
        )

    # S3 filesystem
    if url.scheme.lower() == "s3":
        if not url.netloc:
            raise Exception("You must specify a s3://bucket/ when using s3")
        return S3FS(
            bucket=url.netloc,
            prefix=url.path,
            aws_access_key=s3_key,
            aws_secret_key=s3_secret,
            key_sync_timeout=3
        )


class Scheduler(mesos.Scheduler):
    """Mesos scheduler that is responsible for launching the builder tasks."""

    def __init__(self, task_queue, executor, checkpoint, cpu_limit, mem_limit, args):
        self.task_queue = task_queue
        self.executor = executor
        self.checkpoint_path = checkpoint
        self.cpu = cpu_limit
        self.mem = mem_limit
        self.args = args

        self.running = 0

        self.filesystem = create_filesystem(
            staging_uri=self.args.staging_uri,
            s3_key=self.args.aws_access_key_id,
            s3_secret=self.args.aws_secret_access_key
        )

    def registered(self, driver, frameworkId, masterInfo):
        logger.info("Framework registered with %s", frameworkId.value)
        self._checkpoint(frameworkId=frameworkId.value)

    def resourceOffers(self, driver, offers):

        if self.task_queue.empty():
            return

        logger.debug("Received %d offers", len(offers))

        for offer in offers:
            offer_cpu = 0.0
            offer_mem = 0

            for resource in offer.resources:
                if resource.name == "cpus":
                    offer_cpu = resource.scalar
                if resource.name == "mem":
                    offer_mem = resource.scalar

            # Launch the task if applicable
            if offer_cpu >= self.cpu and offer_mem >= self.mem:
                try:
                    self._launchTask(driver, self.task_queue.get(), offer)
                except Exception, e:
                    logger.error("Caught exception launching task %r", e)
                    self.task_queue.task_done()
            else:
                logger.debug("Ignoring offer %r", offer)

    def statusUpdate(self, driver, update):

        logger.debug("Received task status update")

        done = False

        if update.state == mesos_pb2.TASK_FAILED:
            logger.info("Task update : FAILED")
            done = True
        elif update.state == mesos_pb2.TASK_FINISHED:
            logger.info("Task update : FINISHED")
            done = True
        elif update.state == mesos_pb2.TASK_KILLED:
            logger.info("Task update : KILLED")
            done = True
        elif update.state == mesos_pb2.TASK_LOST:
            logger.info("Task update : LOST")
            done = True

        if done:
            self.task_queue.task_done()
            self.running -= 1

        if self.running == 0 and self.task_queue.empty():
            driver.stop()

    def _launchTask(self, driver, dockerfile_path, offer):

        logger.info("Prepping task to build %s", dockerfile_path)

        # Parse the dockerfile
        context_root = os.path.abspath(os.path.dirname(dockerfile_path))
        dockerfile = parse_dockerfile(dockerfile_path)

        # Generate the dockerfile build context
        _, context_path = tempfile.mkstemp()
        context = open(context_path, "w+b")

        logger.debug("Writing context tar to %s", context_path)

        context_size = make_build_context(context, context_root, dockerfile)

        # Generate a task ID
        task_id = str(uuid.uuid1())
        staging_file = os.path.join(task_id, "docker_context.tar.gz")

        # Upload the build context to the staging filesystem
        logger.debug("Task staging directory %s", os.path.join(self.args.staging_uri, task_id))
        logger.info("Uploading context (%d bytes)", context_size)

        # Create the directory
        self.filesystem.makedir(task_id, recursive=True)

        # Create a progress bar
        pbar = progressbar.ProgressBar(maxval=context_size)
        event = self.filesystem.setcontents_async(
            path=staging_file,
            data=context,
            progress_callback=pbar.update,
            finished_callback=pbar.finish
        )

        # Wait for the file to upload...
        event.wait()

        # Close and clear up the tmp context
        logger.info("Cleaning up local context %s", context_path)
        context.close()
        os.unlink(context_path)

        # Define the docker image
        image = ddocker_pb2.DockerImage()

        try:
            user, repo = dockerfile.get("REPOSITORY").next().pop().split("/")
            image.repository.username = user
            image.repository.repo_name = repo
        except StopIteration:
            raise KeyError("No REPOSITORY found in %s" % dockerfile_path)

        try:
            registry = dockerfile.get("REGISTRY").next().pop().split(":")
            image.registry.hostname = registry[0]
            if len(registry) > 1:
                image.registry.port = int(registry[1])
        except StopIteration:
            raise KeyError("No REGISTRY found in %s" % dockerfile_path)

        image.tag.extend(map(lambda t: t[0], dockerfile.get("TAG")))

        # Launch the mesos task!
        task = mesos_pb2.TaskInfo()
        task.name = "build"
        task.task_id.value = task_id
        task.slave_id.value = offer.slave_id.value
        task.command.value = "sleep 5"  # Empty value to allow us to use command URIs below

        uri = task.command.uris.add()
        uri.value = os.path.join(self.args.staging_uri, staging_file)

        # task.data = image.SerializeToString()
        # task.executor.MergeFrom(self.executor)

        # Build up the resources
        cpu_resource = task.resources.add()
        cpu_resource.name = "cpus"
        cpu_resource.type = mesos_pb2.Value.SCALAR
        cpu_resource.scalar.value = self.cpu

        mem_resource = task.resources.add()
        mem_resource.name = "mem"
        mem_resource.type = mesos_pb2.Value.SCALAR
        mem_resource.scalar.value = self.mem

        logger.info("Launching task to build %s", dockerfile_path)

        driver.launchTasks(offer.id, [task])

        self.running += 1

    def _checkpoint(self, frameworkId=None):
        """Helper method for persisting checkpoint information."""

        if not self.checkpoint_path:
            logger.debug("Skipping checkpoint, not enabled")
            return

        exists = os.path.exists(self.checkpoint_path)
        with open(self.checkpoint_path, "w+b") as cp:
            checkpoint = ddocker_pb2.Checkpoint()
            if exists:
                ddocker_pb2.Checkpoint.ParseFromString(checkpoint, cp.read())
                cp.seek(0)

            if frameworkId:
                checkpoint.frameworkId = frameworkId

            logger.debug("Written checkpoint to %s", self.checkpoint_path)

            cp.write(checkpoint.SerializeToString())
            cp.truncate()