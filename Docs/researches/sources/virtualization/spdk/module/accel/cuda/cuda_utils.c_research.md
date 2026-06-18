# File Research: sources/virtualization/spdk/module/accel/cuda/cuda_utils.c

## Purpose

Provides process-wide CUDA host-memory registration support through SPDK memory-map notifications.

## Main Responsibilities

- Registers memory with CUDA on SPDK memory-map register notifications using `cudaHostRegister(..., cudaHostRegisterMapped)`.
- Unregisters memory on unregister notifications with `cudaHostUnregister`.
- Maintains one global `cuda_mem_map` with reference counting.
- Provides:
  - `cuda_utils_create_mem_map`
  - `cuda_utils_free_mem_map`

## Key Data

- `struct cuda_mem_map`: SPDK mem map pointer plus refcount.
- `g_cuda_mem_map`: singleton map.
- `g_cuda_maps_mutex`: protects singleton/refcount.

## Dependencies

- CUDA Runtime API.
- SPDK `spdk_mem_map_alloc/free` notification mechanism.

## Notes / Risks

- All CUDA accel users share a single process-wide map.
- Registration failures return `-ENOMEM`, so memory-map creation can fail if CUDA cannot register an existing SPDK memory range.
