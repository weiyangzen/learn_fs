# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibci.h

## Purpose

`ibci.h` defines the InfiniBand Channel Interface between IBTF/IBTL and HCA driver implementations. It is the driver-side contract: HCA drivers register their capability data and operation vector with IBTF, while IBTF calls through the vector to allocate, modify, query, post, poll, map, and free transport resources.

## Main Interfaces

The header defines opaque handles for both directions: IBTF-visible CI handles such as `ibc_hca_hdl_t`, `ibc_pd_hdl_t`, `ibc_qp_hdl_t`, `ibc_cq_hdl_t`, `ibc_srq_hdl_t`, memory-region/window handles, and CI-visible IBTF handles such as `ibtl_qp_hdl_t`, `ibtl_eec_hdl_t`, and `ibc_clnt_hdl_t`.

The central type is `ibc_operations_t`, a large HCA driver vtable. It covers HCA and port query/modify operations, protection domains, RDD/EEC legacy reliable datagram objects, address handles, QP allocation/free/query/modify including special and range allocation, CQ allocation/resizing/moderation/scheduling, memory registration and synchronization, memory windows, multicast attach/detach, send/receive posting, CQ polling/notification, CI private data import/export, SRQs, address translation, L_Key allocation, physical and DMA memory registration, FMR pools, IO memory allocation, and XRC placeholders.

`ibc_hca_info_t` packages the CI version, driver HCA handle, operation vector, and static HCA attributes supplied during attach.

## Upcalls

The CI calls into IBTF through `ibc_init()`, `ibc_fini()`, `ibc_attach()`, `ibc_post_attach()`, `ibc_pre_detach()`, `ibc_detach()`, `ibc_cq_handler()`, `ibc_async_handler()`, `ibc_memory_handler()`, and `ibc_get_ci_failure()`.

## Research Notes

This header is central to RDMA storage and network driver behavior because every queue, completion, protection-domain, and memory-registration operation eventually crosses this ABI. Correctness depends on strict handle ownership, persistent `hca_ops`/`hca_attr` storage, and consistent translation between IBTF channel abstractions and HCA-native objects.
