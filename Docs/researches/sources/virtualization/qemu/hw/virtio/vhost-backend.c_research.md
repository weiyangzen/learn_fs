# File Research: sources/virtualization/qemu/hw/virtio/vhost-backend.c

## Purpose
Provides vhost backend operations for kernel vhost and common device-IOTLB helper functions.

## Key Behavior
- Under `CONFIG_VHOST_KERNEL`, wraps kernel vhost ioctls in `vhost_kernel_call()`.
- Implements kernel backend init, cleanup, memslot limit discovery, feature get/set, owner setup, vring configuration, eventfd setup, SCSI endpoint operations, vsock operations, and worker operations.
- Supports extended feature arrays with fallback to legacy `VHOST_GET/SET_FEATURES`.
- Reads `/sys/module/vhost/parameters/max_mem_regions`, defaulting to 64 on failure or invalid values.
- Negotiates `VHOST_BACKEND_F_IOTLB_MSG_V2` when available.
- Reads kernel IOTLB miss/access messages from the vhost fd and forwards them to generic vhost handling.
- Sends device IOTLB update/invalidate messages in v1 or v2 message formats depending on backend capability.
- Exposes `kernel_ops` as the `VhostOps` table.
- Provides backend-independent helpers for updating, invalidating, and handling device IOTLB messages.

## Filesystem/Storage Relevance
Kernel vhost accelerates virtio storage/network paths. The IOTLB plumbing is especially important for IOMMU-backed DMA correctness in vhost storage and filesystem devices.
