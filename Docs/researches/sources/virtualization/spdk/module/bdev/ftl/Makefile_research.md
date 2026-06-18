# File Research: sources/virtualization/spdk/module/bdev/ftl/Makefile

## Purpose
Builds the SPDK FTL bdev module library.

## Main Contents
The makefile sets `SPDK_ROOT_DIR`, includes SPDK common/lib make fragments, declares shared-object version `8.0`, adds `lib/ftl` to include paths, compiles `bdev_ftl.c` and `bdev_ftl_rpc.c`, names the library `bdev_ftl`, and uses `spdk_blank.map`.

## Dependencies
Depends on the SPDK make infrastructure and the FTL library headers.

## Risks and Notes
This is a thin build declaration; source membership and the extra FTL include path are the main maintenance points.
