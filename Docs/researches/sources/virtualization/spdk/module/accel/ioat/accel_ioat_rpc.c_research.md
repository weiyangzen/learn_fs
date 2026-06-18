# File Research: sources/virtualization/spdk/module/accel/ioat/accel_ioat_rpc.c

## Purpose

Defines startup RPC for enabling the IOAT accel module.

## Key Contents

- RPC handler `rpc_ioat_scan_accel_module`.
- Rejects non-null params.
- Logs enablement, calls `accel_ioat_enable_probe()`, returns JSON boolean `true`.
- Registers:
  - `ioat_scan_accel_module`
  - startup phase only.

## Relationships

- Uses `accel_ioat.h`.
