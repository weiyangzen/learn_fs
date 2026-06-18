# File Research: sources/virtualization/spdk/module/accel/cuda/cuda_utils.h

## Purpose

Header for CUDA memory-map helper API.

## Key Contents

- Opaque `struct cuda_mem_map`.
- Declares:
  - `struct cuda_mem_map *cuda_utils_create_mem_map(void);`
  - `void cuda_utils_free_mem_map(struct cuda_mem_map **map);`
- C++ compatible `extern "C"` block.

## Relationships

- Used by `accel_cuda.c` and implemented by `cuda_utils.c`.
