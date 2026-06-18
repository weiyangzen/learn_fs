# File Research: sources/virtualization/qemu/hw/virtio/vhost-user-input.c

## Purpose
Defines a vhost-user input device using `VHostUserBase`.

## Key Behavior
- Exposes a `chardev` property.
- Sets virtio ID `VIRTIO_ID_INPUT`.
- Uses two virtqueues, queue size 4, and config size `virtio_input_config`.
- Marks VMState unmigratable.
- Registers input device category.

## Filesystem/Storage Relevance
No direct filesystem role; shares the same base-class data path lifecycle used by simpler vhost-user devices.
