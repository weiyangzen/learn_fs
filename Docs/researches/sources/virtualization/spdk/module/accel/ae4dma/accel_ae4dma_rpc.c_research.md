# File Research: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma_rpc.c

## Purpose

Defines the startup RPC for enabling the AE4DMA accel module.

## Key Contents

- RPC handler `rpc_ae4dma_scan_accel_module`.
- Rejects any non-null parameters.
- Logs enablement, calls `accel_ae4dma_enable_probe()`, and returns JSON boolean `true`.
- Registers RPC:
  - `ae4dma_scan_accel_module`
  - startup phase only.

## Relationships

- Calls the enable function declared in `accel_ae4dma.h`.
