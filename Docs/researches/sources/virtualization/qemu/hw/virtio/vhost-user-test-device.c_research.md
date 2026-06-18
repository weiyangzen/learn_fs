# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-test-device.c

## Purpose
Defines a concrete configurable vhost-user device for development and prototyping.

## Key Behavior
- Subclasses `VHostUserBase`.
- Lets users provide `chardev`, `virtio-id`, `vq_size`, `num_vqs`, and `config_size` properties.
- Leaves backend-specific configuration to the external vhost-user daemon.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
Can be used to prototype vhost-user devices, including storage-like devices, without adding a dedicated QEMU device model first.
