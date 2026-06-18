# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-snd.c

## Purpose
Defines vhost-user sound as a `VHostUserBase` specialization.

## Key Behavior
- Supports optional `VIRTIO_SND_F_CTLS` via a `controls` property that sets a host feature bit.
- Computes config size from feature-dependent virtio sound config bounds.
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_SOUND`.
- Uses four virtqueues and queue size 64.
- Marks VMState unmigratable and registers sound category.

## Filesystem/Storage Relevance
No direct filesystem role; shows feature-dependent config sizing in a vhost-user-base device.
