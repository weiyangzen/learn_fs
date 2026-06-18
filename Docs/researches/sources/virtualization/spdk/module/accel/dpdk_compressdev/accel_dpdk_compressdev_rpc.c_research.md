# File Research: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev_rpc.c

## Purpose

Defines startup RPC for enabling/configuring the DPDK compressdev accel module.

## Key Contents

- Decodes `pmd` from `rpc_compressdev_scan_accel_module_ctx`.
- Validates `pmd < COMPRESS_PMD_MAX`.
- Calls `accel_compressdev_enable_probe(&req.pmd)`.
- Calls `accel_dpdk_compressdev_enable()`.
- Returns JSON boolean `true`.
- Registers:
  - `compressdev_scan_accel_module`
  - startup phase only.

## Relationships

- Uses generated RPC context from `spdk_internal/rpc_autogen.h`.
- Calls API from `accel_dpdk_compressdev.h`.
