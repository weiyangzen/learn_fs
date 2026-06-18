# File Research: sources/virtualization/spdk/lib/mlx5/Makefile

Builds SPDK's mlx5 support library.

Key contents:
- Sets `SPDK_ROOT_DIR` and includes `mk/spdk.common.mk`.
- Declares ABI version `SO_VER := 5` and `SO_MINOR := 0`.
- Builds `mlx5_crypto.c`, `mlx5_qp.c`, `mlx5_dma.c`, and `mlx5_umr.c` into `LIBNAME = mlx5`.
- Links system libraries `-lmlx5` and `-libverbs`.
- Uses `spdk_mlx5.map` as the export map and includes `mk/spdk.lib.mk`.

Filesystem/block relevance:
- The mlx5 library provides low-level RDMA, DMA, memory-key, and crypto offload support that SPDK storage transports and bdev modules can use for high-performance data movement.
