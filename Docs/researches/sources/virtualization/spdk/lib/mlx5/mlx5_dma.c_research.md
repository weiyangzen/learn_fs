# File Research: sources/virtualization/spdk/lib/mlx5/mlx5_dma.c

Implements low-level mlx5 queue-pair RDMA read/write WQE construction, send completion doorbell handling, CQ polling, CQE error decoding, and debug WQE dumping.

Key entry points:
- `spdk_mlx5_qp_rdma_write()` and `spdk_mlx5_qp_rdma_read()` post RDMA write/read work requests through a shared `mlx5_qp_rdma_op()` helper.
- `spdk_mlx5_cq_poll_completions()` polls send completions and returns work request IDs plus completion status.
- `spdk_mlx5_qp_complete_send()` rings the send doorbell and handles last-signaled mode completion accounting.
- `mlx5_qp_dump_wqe()` dumps raw WQE building blocks under `DEBUG` when the `mlx5_sq` log flag is enabled.

Core mechanics:
- WQEs are built directly in the mlx5 send queue as control segment, remote address segment, and one data segment per SGE.
- `mlx5_qp_rdma_op()` computes the number of 64-byte WQE building blocks needed: one block covers control, remote address, and up to two SGEs; additional SGEs consume more blocks.
- The code checks both available SQ building blocks and `qp->max_send_sge` before writing the WQE.
- `mlx5_dma_xfer_full()` handles WQEs that fit contiguously before the end of the circular SQ.
- `mlx5_dma_xfer_wrap_around()` writes segment-by-segment and wraps data segments to the beginning of the SQ when needed.
- After WQE construction, `mlx5_qp_wqe_submit()` advances producer state and `mlx5_qp_set_comp()` records completion metadata indexed by producer index.
- `mlx5_qp_tx_complete()` updates completion aggregation for `SPDK_MLX5_QP_SIG_LAST` and rings the queue doorbell.
- CQ polling checks ownership and opcode validity, finds the originating QP by QPN, converts CQEs to SPDK completion records, and restores `tx_available` from recorded completion counts.

Error handling:
- `_mlx5_err_cqe` and `mlx5_sigerr_cqe` model mlx5 error CQE layouts.
- `mlx5_cqe_err_opcode()` decodes the failed WQE opcode into readable operation names.
- `mlx5_cqe_err()` maps mlx5 CQE syndromes to diagnostic text, treats flushed work requests as debug-level, and logs other CQE failures as warnings with QP number, WQE index, syndrome, vendor syndrome, hardware syndrome, and opcode.

Important invariants:
- Send queue size is treated as a power-of-two ring and producer indices are masked with `sq_wqe_cnt - 1`.
- `qp->tx_available` must be at least the WQE building block count before posting and is decremented after posting.
- Completion records are indexed by WQE counter masked to the SQ size.
- Unsignaled work requests are accumulated into the next signaled completion.
- CQ consumer index is advanced only after owner/opcode checks pass.

Filesystem/block relevance:
- This file is data-plane infrastructure for SPDK's RDMA/mlx5 paths. It does not implement filesystem logic, but it directly affects block-storage transport throughput and correctness for RDMA reads/writes.

Notable risks:
- Direct WQE construction is layout-sensitive and depends on mlx5 hardware ABI structures and endian conversions being correct.
- Wrap-around WQE construction must update `to_end` exactly or it can corrupt the SQ ring.
- `spdk_mlx5_cq_poll_completions()` returns `-ENODEV` if a CQE's QPN cannot be mapped to a known QP, which can abort polling even if later CQEs are valid.
