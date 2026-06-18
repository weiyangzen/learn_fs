# File Research: sources/virtualization/spdk/lib/rdma_cm/Makefile

This Makefile builds SPDK’s `rdma_cm` shim library with shared object version `1.0` and map file `spdk_rdma_cm.map`.

The selected source depends on `CONFIG_RDMA_CM`: `cma` builds `rdma_cm_cma.c` and links `-libverbs -lrdmacm`, while `mock` builds `rdma_cm_mock.c` with no RDMA CM system library dependency. Any other value is a hard make error.

On FreeBSD, if RDMA is configured and vendor userspace libraries are present under `/usr/lib`, the Makefile adds optional provider libraries for Mellanox mlx4, Mellanox mlx5, and Chelsio cxgb4. It then includes the standard SPDK library make rules.
