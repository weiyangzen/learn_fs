# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-gpio.c

## Purpose
Defines the vhost-user GPIO virtio device as a `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets fixed virtio ID `VIRTIO_ID_GPIO`.
- Uses two virtqueues.
- Sets config size to `struct virtio_gpio_config`.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
No direct filesystem role; useful as a compact example of vhost-user-base device specialization.
