# File Research: sources/virtualization/spdk/module/bdev/lvol/Makefile

## Purpose
Builds the SPDK logical-volume bdev module library.

## Main Contents
Declares shared-object version `8.0`, compiles `vbdev_lvol.c` and `vbdev_lvol_rpc.c`, names the library `bdev_lvol`, uses `spdk_blank.map`, and includes SPDK common/lib make fragments.

## Dependencies
Depends on the SPDK make infrastructure and lvol/blob/bdev headers used by the sources.

## Risks and Notes
This build unit contains both core lvol logic and the RPC surface; no separate RPC library is declared.
