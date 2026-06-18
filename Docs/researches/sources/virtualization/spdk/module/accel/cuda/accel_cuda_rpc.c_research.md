# File Research: sources/virtualization/spdk/module/accel/cuda/accel_cuda_rpc.c

## Purpose

Defines startup RPC for enabling the CUDA accel module.

## Key Contents

- RPC handler `rpc_cuda_scan_accel_module`.
- Rejects non-null params.
- Logs enablement, calls `accel_cuda_enable_probe()`, returns JSON boolean `true`.
- Registers:
  - `cuda_scan_accel_module`
  - startup phase only.

## Relationships

- Calls `accel_cuda_enable_probe()` from `accel_cuda.h`.
