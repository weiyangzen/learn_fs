# File Research: sources/virtualization/qemu/hw/virtio/vhost-stub.c

## Purpose
Provides stub implementations when full vhost/vhost-user support is not built.

## Key Behavior
- Reports unlimited maximum/free memslots with `UINT_MAX`.
- Makes `vhost_user_init()` fail.
- Provides no-op cleanup and device-IOTLB toggle functions.

## Filesystem/Storage Relevance
Allows non-vhost QEMU builds to link while making vhost-user devices unavailable.
