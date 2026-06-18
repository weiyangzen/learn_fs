# File Research: sources/virtualization/spdk/module/event/subsystems/bdev/bdev.c

Registers the SPDK bdev framework as an event subsystem.

Key elements:
- Initializes bdev through `spdk_bdev_initialize()` and completion callback.
- Finishes through `spdk_bdev_finish()`.
- Emits bdev subsystem config JSON through `spdk_bdev_subsystem_config_json()`.
- Registers subsystem name `bdev`.

Dependencies:
- Declares dependencies on accel, keyring, vmd, sock, and iobuf.

Research notes:
- Provides the central block-storage lifecycle dependency for NBD, NVMe-oF, ublk, vhost block, and SCSI consumers.
