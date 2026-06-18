# File Research: sources/virtualization/spdk/module/accel/dpdk_cryptodev/Makefile

## Purpose

Builds the DPDK cryptodev accel module.

## Key Contents

- Adds `$(ENV_CFLAGS)`.
- `LIBNAME = accel_dpdk_cryptodev`
- Sources:
  - `accel_dpdk_cryptodev.c`
  - `accel_dpdk_cryptodev_rpc.c`
- Shared object version: `SO_VER := 5`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_CRYPTO`.
