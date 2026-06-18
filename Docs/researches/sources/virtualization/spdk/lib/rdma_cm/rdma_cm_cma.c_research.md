# File Research: sources/virtualization/spdk/lib/rdma_cm/rdma_cm_cma.c

This file implements the real RDMA CM backend for SPDK’s internal `spdk_rdma_cm_*` wrapper API. Most functions are direct one-to-one pass-throughs to `librdmacm`: event channel create/destroy, ID create/destroy, option setting, bind/resolve route/connect/listen/accept/reject/disconnect, CM event get/ack, QP create/destroy, source/destination port retrieval, and device list get/free.

The wrapper exists so the rest of SPDK can depend on `spdk_internal/rdma_cm.h` without directly selecting between real and mock RDMA CM implementations.

Two functions are explicitly unsupported on FreeBSD. `spdk_rdma_cm_init_qp_attr()` and `spdk_rdma_cm_establish()` set `errno = ENOTSUP` and return `-1` under `__FreeBSD__`; otherwise they call `rdma_init_qp_attr()` and `rdma_establish()`.

The main invariant is preserving `librdmacm` return/errno behavior so higher-level RDMA transport code can use the wrapper as if it were calling RDMA CM directly, except where FreeBSD lacks support.
