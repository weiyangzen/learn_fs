# File Research: sources/virtualization/spdk/module/accel/iaa/Makefile

## Purpose

Builds the Intel IAA accel module.

## Key Contents

- `LIBNAME = accel_iaa`
- Sources:
  - `accel_iaa.c`
  - `accel_iaa_rpc.c`
- Shared object version: `SO_VER := 5`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_IDXD`.
