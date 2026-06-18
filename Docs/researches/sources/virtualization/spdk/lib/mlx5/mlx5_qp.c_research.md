# File Research: sources/virtualization/spdk/lib/mlx5/mlx5_qp.c

Implements SPDK mlx5 completion queue and reliable-connected QP creation using mlx5 direct verbs/devx, then self-connects QPs in loopback mode for local offload work.

Key behavior:
- `spdk_mlx5_cq_create` allocates a CQ with `mlx5dv_create_cq`, exports direct CQ buffer metadata with `mlx5dv_init_obj`, and records CQ address/count/size/CQN.
- `spdk_mlx5_qp_create` creates an RC QP with standard verbs send ops plus mlx5 MKEY configure support, extracts direct SQ/doorbell/BlueFlame mappings, allocates per-WQEBB completion records, connects the QP, and registers it in the CQ QPN lookup table.
- `mlx5_fill_qp_conn_caps` queries HCA and RoCE capabilities to decide whether force-loopback is allowed, including NVMe emulation manager and RoCE-specific flags.
- `mlx5_check_port` supports local InfiniBand addressing when GRH is not required and Ethernet/RoCE with MTU 4096.
- QP state transitions are done through devx command buffers: RST2INIT, INIT2RTR, RTR2RTS. This is necessary because once devx performs RTR transition, the kernel does not know the QP state.
- Destroy paths remove the QP from CQ lookup, destroy verbs objects, and free completion storage.

Dependencies:
- `mlx5_priv.h`, `mlx5_ifc.h`, `infiniband/mlx5dv.h`, SPDK logging/util/assert/RDMA helpers, and libibverbs.

Important APIs:
- `spdk_mlx5_cq_create`, `spdk_mlx5_cq_destroy`
- `spdk_mlx5_qp_create`, `spdk_mlx5_qp_destroy`
- `spdk_mlx5_qp_set_error_state`
- `spdk_mlx5_qp_get_verbs_qp`

Research notes:
- The file is focused on local mlx5 queue setup rather than generic network connectivity.
- CQ destroy refuses to proceed while QPs remain bound.
- Potential issue: `mlx5_cq_init` frees `cq` on `mlx5dv_init_obj` failure even though the caller also frees the object after `mlx5_cq_init` returns an error. That looks like a double-free risk on this error path.
