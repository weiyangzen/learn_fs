# File Research: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_rpc.c

## Purpose
JSON-RPC front-end for virtio block and SCSI controllers.

## RPCs
- `bdev_virtio_blk_set_hotplug`: enables/disables PCI virtio-blk hotplug monitoring.
- `bdev_virtio_detach_controller`: tries virtio-blk removal first, then virtio-scsi removal if no blk device exists.
- `bdev_virtio_scsi_get_devices`: returns all active virtio-scsi devices.
- `bdev_virtio_attach_controller`: creates blk or scsi controllers over PCI, vhost-user, or vfio-user.

## Notable Validation
PCI and vfio-user transports reject `vq_count`/`vq_size`; vhost-user defaults to one queue and queue size 512 when not supplied. PCI transport parses `traddr` as an SPDK PCI address.

Virtio-blk creation is synchronous and the RPC manually invokes the shared completion helper. Virtio-scsi creation is asynchronous and returns through the scan callback.
