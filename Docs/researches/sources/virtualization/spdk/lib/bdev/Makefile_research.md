# File Research: sources/virtualization/spdk/lib/bdev/Makefile

This Makefile builds the SPDK `bdev` library. It includes `bdev.c`, `bdev_rpc.c`, `bdev_zone.c`, `part.c`, and `scsi_nvme.c`, and conditionally includes `vtune.c` when `CONFIG_VTUNE` is enabled.

It sets shared-object version `20.0`, `LIBNAME = bdev`, and uses `spdk_bdev.map` as the symbol map.

Research notes: the listed group covers support files in this library but not the main `bdev.c`, which is still part of the build through this Makefile.
