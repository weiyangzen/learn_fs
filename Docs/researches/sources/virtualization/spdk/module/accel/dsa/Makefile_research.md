# File Research: sources/virtualization/spdk/module/accel/dsa/Makefile

## Purpose

Builds the Intel DSA accel module.

## Key Contents

- `LIBNAME = accel_dsa`
- Sources:
  - `accel_dsa.c`
  - `accel_dsa_rpc.c`
- Shared object version: `SO_VER := 7`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_IDXD`.
