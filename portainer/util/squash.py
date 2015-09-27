import tarfile
import json
import tempfile
import os

from .fs import touch, mkdir_p


def get_squash_layers(docker, base_image_id, head_image_id):
    """
    get_squash_layers will return an ordered list of the layers between `base_image_id`
    and `head_image_id`, including `head_image_id`. This list can be used to determine
    the layers that should be squashed together. For example, given this image
    lineage;

    [A] <- [B] <- [C] <- [D]

    get_squash_layers(base = A, head = D) would return [D, C, B]

    The function will return a tuple of the following items;
     - Base Image ID
     - Head Image ID
     - Size of all layers in bytes
     - Ordered list of layers (top-down)
    """

    # Pull out the full image IDs from the docker API, we might be given
    # short hashes so we need to be sure we have the full ones. This also
    # serves as a nice check to be sure the images exist in the docker
    # daemon.
    head_image_id = docker.inspect_image(head_image_id)["Id"]
    base_image_id = docker.inspect_image(base_image_id)["Id"]

    layers = []
    aggregate_size = 0

    for layer in json.loads(docker.history(head_image_id)):
        if layer["Id"] == base_image_id:
            break
        layers.append(layer["Id"])
        aggregate_size += layer["Size"]

    return base_image_id, head_image_id, aggregate_size, layers


def download_layers_for_image(docker, directory, image_id):
    """
    download_layers_for_image downloads all layers for `image_id` from docker
    into a temporary file within `directory` and returns a file handle
    to the tar.

    The temporary file will be deleted once the file handle is closed.
    """

    _, path = tempfile.mkstemp(dir=directory, suffix=".tar")
    fh = open(path, "wb+")
    for chunk in docker.get_image(image_id).stream():
        fh.write(chunk)

    fh.seek(0)
    return fh


def extract_layer_tar(directory, layers_tar, layer_id):
    """
    extract_layer_tar will return an open file handle for the given to a tar
    for the given `layer_id` after extracting it from the given `layers_tar`
    TarFile.

    When exporting an image from docker, it will provide a tar of each layer
    that makes up the image.

    Each layer will be in a folder (with the layer_id as the folder name) and the
    filesystem for that layer will be within another tar. This function will take
    care of locating this nested tar, and extracting it to somewhere temporary.
    """

    layer_member = os.path.join(layer_id, "layer.tar")
    path = tempfile.mkdtemp(dir=directory)

    layers_tar.extract(
        member=layer_member,
        path=path
    )

    return open(os.path.join(path, layer_member))


def apply_layer(directory, layer_tar, seen_paths=set()):
    """
    apply_layer will apply the given `layer_tar` filesystem over the top of the
    given `directory` correctly handling whiteouts based on the paths
    that have already been seen by previous layers.
    """

    for member in layer_tar.getnames():
        parent, leaf = os.path.split(member)

        if member.startswith(".wh..wh."):
            continue
        elif leaf.startswith(".wh."):
            seen_paths.add(os.path.join(parent, leaf[4:]))
            wh_path = os.path.join(directory, member)
            wh_parent = os.path.dirname(wh_path)
            if wh_parent != directory:
                mkdir_p(wh_parent)
            touch(wh_path)
        elif member not in seen_paths:
            layer_tar.extract(member=member, path=directory)
            seen_paths.add(member)

    return seen_paths


def generate_tarball(directory, tar_directory):
    """
    generate_tarball will return a path to a newly generated tarball inside the
    given `directory`, with all of the contents of `tar_directory` within.
    """

    _, tarball_path = tempfile.mkstemp(dir=directory, suffix=".tar")
    tarball = tarfile.open(tarball_path, "w")

    for path in os.listdir(tar_directory):
        tarball.add(os.path.join(tar_directory, path), arcname=path)

    tarball.close()
    return tarball_path


def rewrite_image_parent(image_info, new_parent):
    """
    rewrite_image_parent will change the given image info dictionary to point
    to the `new_parent` image.
    """

    image_info["parent"] = new_parent
    image_info["config"]["Image"] = new_parent
    image_info["container_config"]["Image"] = new_parent

    return image_info
