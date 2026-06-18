# File Research: sources/virtualization/spdk/module/accel/cuda/Makefile

## Purpose

Builds the CUDA accel module library.

## Key Contents

- `LIBNAME = accel_cuda`
- C sources:
  - `accel_cuda.c`
  - `accel_cuda_rpc.c`
  - `cuda_utils.c`
- CUDA source:
  - `accel_cuda_kern.cu`
- Sets `CUDA_ARCH = 70`.
- Shared object version: `SO_VER := 7`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_CUDA`.
- The report group includes headers and C helpers but not the `.cu` implementation file.
