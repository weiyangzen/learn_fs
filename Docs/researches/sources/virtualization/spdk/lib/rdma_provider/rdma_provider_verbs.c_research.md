# File Research: sources/virtualization/spdk/lib/rdma_provider/rdma_provider_verbs.c

This file implements the generic ibverbs RDMA provider.

`spdk_rdma_provider_qp_create()` rejects memory-domain transfer callbacks because the verbs provider does not support that functionality. It allocates the common QP wrapper, uses caller-provided or private stats, creates an RC QP through `spdk_rdma_cm_create_qp()`, stores `cm_id->qp`, obtains a shared SPDK RDMA memory domain for the PD through `spdk_rdma_utils_get_memory_domain()`, and returns negotiated caps.

Accept simply delegates to `spdk_rdma_cm_accept()`, and complete-connect is a no-op for verbs. Destroy warns on queued send WRs, destroys the QP through RDMA CM, frees private stats, releases the shared memory domain through `spdk_rdma_utils_put_memory_domain()`, and frees the wrapper.

Disconnect delegates to `spdk_rdma_cm_disconnect()`, with a special iWARP case: `EINVAL` is accepted as success when the QP is already in an error/disconnect state because iWARP disconnect semantics differ from InfiniBand.

Send queueing appends linked `ibv_send_wr` lists to a pending send queue, counting all submitted WRs and returning true when the queue was previously empty. Flush posts the pending list with `ibv_post_send()`, clears the list, and increments send doorbell updates. Accel sequence support is always false.

The provider is intentionally conservative and relies on RDMA CM for QP creation/destruction and connection state management.
