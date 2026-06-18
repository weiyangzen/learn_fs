# File Research: sources/virtualization/spdk/module/accel/ae4dma/Makefile

## Purpose

Builds the AMD AE4DMA accel module library.

## Key Contents

- `LIBNAME = accel_ae4dma`
- Sources:
  - `accel_ae4dma.c`
  - `accel_ae4dma_rpc.c`
- Shared object version: `SO_VER := 2`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Included when `module/accel/Makefile` selects `ae4dma`.
