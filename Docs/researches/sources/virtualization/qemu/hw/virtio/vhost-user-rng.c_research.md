# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-rng.c

## Purpose
Defines vhost-user RNG as a simple `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_RNG`.
- Uses one virtqueue of size 4.
- Marks VMState unmigratable.
- Registers input category.

## Filesystem/Storage Relevance
No direct filesystem behavior; another minimal vhost-user-base example.
