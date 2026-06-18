# File Research: sources/virtualization/spdk/lib/rdma_provider/rdma_provider_mlx5_dv.c

This file implements the mlx5 Direct Verbs RDMA provider. It uses `mlx5dv_create_qp()` and ibverbs extended QP send operations to support batched send work requests and optional SPDK memory-domain transfer acceleration.

`struct spdk_rdma_mlx5_dv_qp` embeds the common provider QP, stores an RDMA memory-domain context, and caches an `ibv_qp_ex *`. `spdk_rdma_provider_qp_create()` builds a reliable-connected QP with explicit PD and send-op flags, allocates private or shared stats, creates the QP through mlx5dv, obtains the extended QP handle, creates an SPDK RDMA memory domain carrying the ibv PD, and optionally installs a data-transfer callback if mlx5 UMR acceleration support is registered. It returns actual negotiated caps through the init attributes.

Connection setup differs from the generic verbs provider. `rdma_mlx5_dv_init_qpair()` manually transitions the QP through INIT, RTR, and RTS using `spdk_rdma_cm_init_qp_attr()` plus `ibv_modify_qp()`. Accept and complete-connect paths call this initializer before `spdk_rdma_cm_accept()` or `spdk_rdma_cm_establish()`.

Destroy warns on queued send WRs, frees private stats, destroys the ibverbs QP directly, destroys the SPDK memory domain if present, and frees the wrapper. Disconnect first moves the QP to ERR with `ibv_modify_qp()` and then calls RDMA CM disconnect.

Send batching uses the extended WR builder API. The first queued send starts an `ibv_wr_start()` sequence. Each `ibv_send_wr` is translated to `ibv_wr_send`, `ibv_wr_send_inv`, `ibv_wr_rdma_read`, or `ibv_wr_rdma_write`, then has its SGE list attached. Flush calls `ibv_wr_complete()`. If completion fails, no WRs were posted, so `bad_wr` is set to the first queued WR. Statistics track submitted WRs and doorbell updates.

`spdk_rdma_provider_accel_sequence_supported()` reports mlx5 UMR implementer registration status. The key risks are correct QP state transitions, matching extended WR sequences to the queued WR list, and destroying the memory domain only after outstanding users are gone.
