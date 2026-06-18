# File Research: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio.h

Public interface for virtio bdev creation/removal.

Defines callbacks:
- `bdev_virtio_create_cb`: async create/scan completion with created bdev array.
- `bdev_virtio_remove_cb`: async removal completion.

Exposes creation/removal for:
- vhost-user virtio-scsi
- vfio-user virtio-scsi
- PCI virtio-scsi
- vhost-user virtio-blk
- vfio-user virtio-blk
- PCI virtio-blk

Also exposes virtio-scsi device listing and virtio-blk PCI hotplug control.
