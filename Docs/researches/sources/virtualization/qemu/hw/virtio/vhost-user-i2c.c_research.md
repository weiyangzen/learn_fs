# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-i2c.c

## Purpose
Defines the vhost-user I2C virtio device as a `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets fixed virtio ID `VIRTIO_ID_I2C_ADAPTER`.
- Uses one virtqueue with size 4.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
No direct filesystem role; demonstrates a minimal one-queue vhost-user-base device.
