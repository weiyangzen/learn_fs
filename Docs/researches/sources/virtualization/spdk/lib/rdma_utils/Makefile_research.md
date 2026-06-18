# File Research: sources/virtualization/spdk/lib/rdma_utils/Makefile

This Makefile builds the `rdma_utils` library from `rdma_utils.c`, with shared object version `3.0` and map file `spdk_rdma_utils.map`.

It links against `-libverbs`. On FreeBSD, if vendor HCA userspace libraries are present under `/usr/lib`, it conditionally adds `-lmlx4`, `-lmlx5`, and `-lcxgb4`. Standard SPDK common and library make rules provide the rest of the build behavior.
