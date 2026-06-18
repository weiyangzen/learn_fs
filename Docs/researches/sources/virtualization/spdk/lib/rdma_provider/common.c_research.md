# File Research: sources/virtualization/spdk/lib/rdma_provider/common.c

This file provides provider-independent RDMA shared receive queue and receive work-request batching helpers.

`spdk_rdma_provider_srq_create()` allocates a wrapper, either adopts caller-provided shared stats or allocates private stats, then creates an ibverbs SRQ with `ibv_create_srq()`. On failures it logs, frees only private allocations, and returns `NULL`. `spdk_rdma_provider_srq_destroy()` tolerates a null wrapper, warns if receive WRs are still queued, destroys the ibverbs SRQ, frees private stats, and releases the wrapper.

The internal `rdma_queue_recv_wrs()` appends a linked list of `ibv_recv_wr` entries to a provider recv queue and increments submitted-WR statistics for each entry. It returns true if the queue was previously empty. Both SRQ and QP receive queue APIs use this helper.

`spdk_rdma_provider_srq_flush_recv_wrs()` posts queued receive WRs with `ibv_post_srq_recv()`, clears the pending list, and increments doorbell update stats. `spdk_rdma_provider_qp_flush_recv_wrs()` does the same for a QP with `ibv_post_recv()` and per-QP recv stats. Empty queues return success without touching the NIC.

The important invariant is that queued WR linked lists remain intact until flush; after a flush attempt the pending head is cleared and doorbell statistics are incremented regardless of post result.
