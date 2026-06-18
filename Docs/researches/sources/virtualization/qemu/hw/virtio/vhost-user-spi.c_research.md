# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-spi.c

## Purpose
Defines vhost-user SPI as a `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_SPI`.
- Uses one virtqueue of size 4.
- Sets config size to `struct virtio_spi_config`.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
No direct filesystem role; another minimal vhost-user-base specialization.
