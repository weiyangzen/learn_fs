# File Research: sources/virtualization/spdk/module/accel/cuda/accel_cuda.h

## Purpose

Internal header for CUDA accel module configuration and enablement.

## Key Contents

- Header guard `SPDK_ACCEL_MODULE_CUDA_H`.
- Defines:
  - `ACCEL_CUDA_XOR_MIN_BUF_LEN 4096`
  - `ACCEL_CUDA_STREAMS_PER_CHANNEL 4`
- Declares `void accel_cuda_enable_probe(void);`

## Relationships

- Used by CUDA RPC and implementation files.
