# File Research: sources/virtualization/spdk/module/accel/dsa/accel_dsa_rpc.c

## Purpose

Defines startup RPC for enabling the DSA accel module.

## Key Contents

- RPC handler `rpc_dsa_scan_accel_module`.
- Optional parameter:
  - `config_kernel_mode`
- Calls `accel_dsa_enable_probe(req.config_kernel_mode)`.
- Logs whether kernel-mode or user-mode DSA was enabled.
- Returns JSON boolean `true`.
- Registers:
  - `dsa_scan_accel_module`
  - startup phase only.

## Relationships

- Uses generated RPC context from `spdk_internal/rpc_autogen.h`.
