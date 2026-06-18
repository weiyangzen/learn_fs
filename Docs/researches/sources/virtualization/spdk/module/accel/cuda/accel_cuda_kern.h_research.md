# File Research: sources/virtualization/spdk/module/accel/cuda/accel_cuda_kern.h

## Purpose

C/C++ ABI header for CUDA kernel launch wrappers used by `accel_cuda.c`.

## Key Contents

- Header guard `SPDK_ACCEL_CUDA_KERN_H`.
- `extern "C"` wrappers for C++ compilation.
- Defines:
  - `CUDA_CACHE_LINE_SIZE 128`
  - `CUDA_XOR_MAX_SOURCES 16`
- Declares launch functions:
  - `accel_cuda_xor_start`
  - `accel_cuda_copy_start`
  - `accel_cuda_fill_start`

## Relationships

- Implemented by CUDA source `accel_cuda_kern.cu` outside this requested group.
- Called from `accel_cuda.c`.
