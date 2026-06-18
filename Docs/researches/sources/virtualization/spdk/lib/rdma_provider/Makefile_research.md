# File Research: sources/virtualization/spdk/lib/rdma_provider/Makefile

This Makefile builds SPDK’s `rdma_provider` library with shared object version `9.0` and map file `spdk_rdma_provider.map`.

`common.c` is always compiled. `CONFIG_RDMA_PROV=verbs` adds `rdma_provider_verbs.c`; `CONFIG_RDMA_PROV=mlx5_dv` adds `rdma_provider_mlx5_dv.c` and links `-lmlx5`. Any other provider name is a hard make error. The library always links `-libverbs`.

For FreeBSD, the Makefile conditionally links optional HCA provider libraries found under `/usr/lib`: `libmlx4`, `libmlx5`, and `libcxgb4`. It finishes by including standard SPDK library rules.
