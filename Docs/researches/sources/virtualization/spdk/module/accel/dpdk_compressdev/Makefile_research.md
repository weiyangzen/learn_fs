# File Research: sources/virtualization/spdk/module/accel/dpdk_compressdev/Makefile

## Purpose

Builds the DPDK compressdev accel module.

## Key Contents

- Adds `$(ENV_CFLAGS)`.
- `LIBNAME = accel_dpdk_compressdev`
- Sources:
  - `accel_dpdk_compressdev.c`
  - `accel_dpdk_compressdev_rpc.c`
- Shared object version: `SO_VER := 5`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_DPDK_COMPRESSDEV`.
