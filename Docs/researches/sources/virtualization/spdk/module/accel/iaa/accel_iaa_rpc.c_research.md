# File Research: sources/virtualization/spdk/module/accel/iaa/accel_iaa_rpc.c

## Purpose

Defines startup RPC for enabling the IAA accel module.

## Key Contents

- RPC handler `rpc_iaa_scan_accel_module`.
- Rejects non-null params.
- Calls `accel_iaa_enable_probe()`.
- Logs `"Enabled IAA user-mode"`.
- Returns JSON boolean `true`.
- Registers:
  - `iaa_scan_accel_module`
  - startup phase only.

## Relationships

- Uses `accel_iaa.h`.
