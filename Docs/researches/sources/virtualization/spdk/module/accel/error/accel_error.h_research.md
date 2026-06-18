# File Research: sources/virtualization/spdk/module/accel/error/accel_error.h

## Purpose

Header for accel error-injection configuration API.

## Key Contents

- `enum accel_error_inject_type`:
  - `ACCEL_ERROR_INJECT_DISABLE`
  - `ACCEL_ERROR_INJECT_CORRUPT`
  - `ACCEL_ERROR_INJECT_FAILURE`
  - `ACCEL_ERROR_INJECT_MAX`
- `struct accel_error_inject_opts`:
  - opcode
  - type
  - count
  - interval
  - errcode
- Declares:
  - `int accel_error_inject_error(struct accel_error_inject_opts *opts);`
  - `const char *accel_error_get_type_name(enum accel_error_inject_type type);`

## Relationships

- Used by implementation and RPC file.
