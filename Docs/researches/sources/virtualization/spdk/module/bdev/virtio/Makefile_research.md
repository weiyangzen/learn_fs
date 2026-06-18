# File Research: sources/virtualization/spdk/module/bdev/virtio/Makefile

Builds the virtio bdev module.

Key settings:
- Includes SPDK common/lib makefiles.
- Sets `SO_VER := 8`, `SO_MINOR := 0`.
- Compiles `bdev_virtio_blk.c`, `bdev_virtio_scsi.c`, and `bdev_virtio_rpc.c`.
- Produces library `bdev_virtio`.
- Uses blank SPDK map file.

This file only defines build composition.
