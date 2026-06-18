# File Research: sources/virtualization/spdk/module/accel/mlx5/Makefile

## Purpose

Builds the MLX5 accel module library.

## Key Contents

- `LIBNAME = accel_mlx5`
- Sources:
  - `accel_mlx5.c`
  - `accel_mlx5_rpc.c`
- Shared object version: `SO_VER := 5`, `SO_MINOR := 0`.
- Uses blank SPDK map file.
- Adds local system libraries:
  - `-libverbs`
  - `-lmlx5`
- Included through `spdk.lib.mk`.

## Relationships

- Selected by `module/accel/Makefile` when `CONFIG_RDMA_PROV=mlx5_dv`.
- This work item includes only the Makefile, not the MLX5 C implementation.
