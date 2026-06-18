# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-rtc.c

## Purpose
Defines vhost-user RTC/clock as a `VHostUserBase` specialization.

## Key Behavior
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_CLOCK`.
- Uses two virtqueues, no config space, and queue size 1024.
- Marks VMState unmigratable.
- Registers misc device category.

## Filesystem/Storage Relevance
No direct filesystem role; demonstrates a base-class specialization with larger queues and no config region.
