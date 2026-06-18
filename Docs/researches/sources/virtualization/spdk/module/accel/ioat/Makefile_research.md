# File Research: sources/virtualization/spdk/module/accel/ioat/Makefile

## Purpose

Builds the Intel IOAT accel module.

## Key Contents

- `LIBNAME = accel_ioat`
- Sources:
  - `accel_ioat.c`
  - `accel_ioat_rpc.c`
- Shared object version: `SO_VER := 8`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Always selected by `module/accel/Makefile`.
