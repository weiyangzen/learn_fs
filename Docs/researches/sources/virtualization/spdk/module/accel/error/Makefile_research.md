# File Research: sources/virtualization/spdk/module/accel/error/Makefile

## Purpose

Builds the accel error-injection module.

## Key Contents

- `LIBNAME = accel_error`
- Sources:
  - `accel_error.c`
  - `accel_error_rpc.c`
- Shared object version: `SO_VER := 4`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Always selected by `module/accel/Makefile`.
