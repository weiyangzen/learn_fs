# File Research: sources/virtualization/spdk/module/accel/Makefile

## Purpose

Build dispatcher for SPDK accel modules.

## Key Contents

- Always builds `error`, `ioat`, and `ae4dma`.
- Conditionally builds:
  - `dpdk_compressdev` for `CONFIG_DPDK_COMPRESSDEV`
  - `dsa` and `iaa` for `CONFIG_IDXD`
  - `dpdk_cryptodev` for `CONFIG_CRYPTO`
  - `cuda` for `CONFIG_CUDA`
  - `mlx5` when `CONFIG_RDMA_PROV=mlx5_dv`
- Delegates subdir traversal through `spdk.subdirs.mk`.

## Relationships

- Parent is `module/Makefile`.
- Child Makefiles define individual shared/static module libraries.

## Notes

- This file controls which hardware/software accel backends appear in a build.
