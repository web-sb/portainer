# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/ddocker.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='proto/ddocker.proto',
  package='ddocker',
  serialized_pb='\n\x13proto/ddocker.proto\x12\x07\x64\x64ocker\"A\n\tBuildTask\x12#\n\x05image\x18\x01 \x02(\x0b\x32\x14.ddocker.DockerImage\x12\x0f\n\x07\x63ontext\x18\x04 \x01(\t\"\xb9\x01\n\x0b\x44ockerImage\x12\x39\n\nrepository\x18\x01 \x02(\x0b\x32%.ddocker.DockerImage.DockerRepository\x12)\n\x08registry\x18\x02 \x01(\x0b\x32\x17.ddocker.DockerRegistry\x12\x0b\n\x03tag\x18\x03 \x03(\t\x1a\x37\n\x10\x44ockerRepository\x12\x10\n\x08username\x18\x01 \x02(\t\x12\x11\n\trepo_name\x18\x02 \x02(\t\"0\n\x0e\x44ockerRegistry\x12\x10\n\x08hostname\x18\x01 \x02(\t\x12\x0c\n\x04port\x18\x02 \x02(\r')




_BUILDTASK = _descriptor.Descriptor(
  name='BuildTask',
  full_name='ddocker.BuildTask',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='image', full_name='ddocker.BuildTask.image', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='context', full_name='ddocker.BuildTask.context', index=1,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=32,
  serialized_end=97,
)


_DOCKERIMAGE_DOCKERREPOSITORY = _descriptor.Descriptor(
  name='DockerRepository',
  full_name='ddocker.DockerImage.DockerRepository',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='username', full_name='ddocker.DockerImage.DockerRepository.username', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='repo_name', full_name='ddocker.DockerImage.DockerRepository.repo_name', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=230,
  serialized_end=285,
)

_DOCKERIMAGE = _descriptor.Descriptor(
  name='DockerImage',
  full_name='ddocker.DockerImage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='repository', full_name='ddocker.DockerImage.repository', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='registry', full_name='ddocker.DockerImage.registry', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tag', full_name='ddocker.DockerImage.tag', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_DOCKERIMAGE_DOCKERREPOSITORY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=100,
  serialized_end=285,
)


_DOCKERREGISTRY = _descriptor.Descriptor(
  name='DockerRegistry',
  full_name='ddocker.DockerRegistry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='hostname', full_name='ddocker.DockerRegistry.hostname', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='port', full_name='ddocker.DockerRegistry.port', index=1,
      number=2, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=287,
  serialized_end=335,
)

_BUILDTASK.fields_by_name['image'].message_type = _DOCKERIMAGE
_DOCKERIMAGE_DOCKERREPOSITORY.containing_type = _DOCKERIMAGE;
_DOCKERIMAGE.fields_by_name['repository'].message_type = _DOCKERIMAGE_DOCKERREPOSITORY
_DOCKERIMAGE.fields_by_name['registry'].message_type = _DOCKERREGISTRY
DESCRIPTOR.message_types_by_name['BuildTask'] = _BUILDTASK
DESCRIPTOR.message_types_by_name['DockerImage'] = _DOCKERIMAGE
DESCRIPTOR.message_types_by_name['DockerRegistry'] = _DOCKERREGISTRY

class BuildTask(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _BUILDTASK

  # @@protoc_insertion_point(class_scope:ddocker.BuildTask)

class DockerImage(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class DockerRepository(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _DOCKERIMAGE_DOCKERREPOSITORY

    # @@protoc_insertion_point(class_scope:ddocker.DockerImage.DockerRepository)
  DESCRIPTOR = _DOCKERIMAGE

  # @@protoc_insertion_point(class_scope:ddocker.DockerImage)

class DockerRegistry(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _DOCKERREGISTRY

  # @@protoc_insertion_point(class_scope:ddocker.DockerRegistry)


# @@protoc_insertion_point(module_scope)
