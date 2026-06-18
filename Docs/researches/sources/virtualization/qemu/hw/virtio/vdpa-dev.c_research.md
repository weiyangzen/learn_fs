# File Research: sources/virtualization/qemu/hw/virtio/vdpa-dev.c

## Purpose
Implements generic vDPA-based virtio device assignment.

## Key Behavior
- Requires a `vhostdev` path and opens it read/write.
- Queries the vDPA device ID, maximum vring size, queue count, and config size through vhost-vDPA ioctls.
- Validates `queue-size` against backend limits and defaults to the backend maximum when unset.
- Initializes a `vhost_dev` with `VHOST_BACKEND_TYPE_VDPA` and a shared vDPA state containing the device fd and IOVA range.
- Fetches device configuration before calling `virtio_init()`.
- Creates one virtio queue per backend queue, using a dummy output handler because the vhost backend handles data path work.
- Implements start/stop through host notifier enablement, guest notifier binding, `vhost_dev_start()`, queue unmasking, and corresponding cleanup.
- Filters `VIRTIO_F_IOMMU_PLATFORM` based on the frontend-requested feature set.
- Marks the VMState as unmigratable.

## Filesystem/Storage Relevance
Generic vDPA assignment can expose hardware or kernel-accelerated virtio storage/network devices to guests while QEMU manages virtio transport, configuration, notifiers, and lifecycle.
