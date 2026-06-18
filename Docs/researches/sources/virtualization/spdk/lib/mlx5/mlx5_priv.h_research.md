# File Research: sources/virtualization/spdk/lib/mlx5/mlx5_priv.h

Private mlx5 helper header shared by SPDK's mlx5 QP and UMR implementation. It defines low-level CQ/QP software mirrors, completion tracking, signature policy, WQE helper structures, and inline doorbell/WQE routines.

Key contents:
- `mlx5_hw_cq` and `mlx5_hw_qp` hold direct mapped CQ/SQ addresses, doorbell records, queue sizes, indices, and QP/CQ numbers.
- `spdk_mlx5_cq` contains a two-level QPN lookup table used to map CQEs back to `spdk_mlx5_qp`.
- `spdk_mlx5_qp` tracks direct-verbs QP state, WQE completion metadata, outstanding unsignaled WQEs, SQ availability, and signal mode.
- Completion mode table maps SPDK signal policy to mlx5 control-segment CE bits.
- Defines crypto BSF, signature BSF, inline signature fields, and SET_PSV WQE segment layouts used by UMR and protection-information code.
- Inline helpers compute current/next WQEBB, store completion metadata, update/ring doorbells, set mlx5 control segments, find QP by QPN, and get PD number via `mlx5dv_init_obj`.

Dependencies:
- `infiniband/mlx5dv.h`, SPDK queue/barrier/likely helpers, and `spdk_internal/mlx5.h`.
- Architecture-specific store fencing for x86 and AArch64.

Research notes:
- Doorbell ordering is carefully staged: CPU write barrier, doorbell record write, bus store fence, then BlueFlame/UAR write.
- `SPDK_MLX5_QP_SIG_LAST` is implemented by mapping most CQ update requests to no-flush-error until the caller submits the final WQE.
- The QPN lookup table assumes mlx5 QPNs are 24-bit and splits upper/lower 12 bits.
- Scope relevance is high: this is the shared fast-path substrate for SPDK mlx5 queue submission and completion.
