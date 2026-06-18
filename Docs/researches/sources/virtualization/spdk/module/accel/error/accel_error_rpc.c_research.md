# File Research: sources/virtualization/spdk/module/accel/error/accel_error_rpc.c

## Purpose

Defines runtime RPC for configuring accel error injection.

## Key Contents

- RPC handler `rpc_accel_error_inject_error`.
- Decodes:
  - `opcode`
  - `type`
  - optional `count`
  - optional `interval`
  - optional `errcode`
- Defaults `count` to `UINT64_MAX`.
- Converts generated RPC context into `accel_error_inject_opts`.
- Calls `accel_error_inject_error`.
- Returns JSON boolean `true`.
- Registers:
  - `accel_error_inject_error`
  - runtime phase.

## Relationships

- Uses generated decoders for accel opcode and injection type.
