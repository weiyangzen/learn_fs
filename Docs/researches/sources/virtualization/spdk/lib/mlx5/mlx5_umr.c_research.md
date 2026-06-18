# File Research: sources/virtualization/spdk/lib/mlx5/mlx5_umr.c

Implements mlx5 UMR and MKEY pool support for SPDK, including ordinary scatter-gather remapping, crypto BSF, signature BSF, PSV creation, and SET_PSV WQE submission.

Key behavior:
- Maintains global MKEY pools keyed by protection domain and flags, protected by `g_mkey_pool_lock`.
- Creates devx MKEY objects with KLM/KLMFBS access modes, local/remote read-write permissions, UMR enablement, relaxed ordering, optional crypto, and optional BSF sizing.
- Uses SPDK mempools to hand out `spdk_mlx5_mkey_pool_obj` wrappers and an RB tree for MKEY lookup within a pool.
- Queries relaxed-ordering HCA capabilities and applies relaxed read/write settings to created MKEYs.
- Builds UMR WQEs in three variants:
  - plain UMR with inline KLM translation entries,
  - crypto UMR with a 64-byte crypto BSF segment,
  - signature UMR with a signature BSF segment and signature-error count toggling.
- Handles SQ wraparound by writing WQEBBs through `mlx5_qp_get_next_wqebb`.
- Creates/destroys PSV objects and submits SET_PSV WQEs with transient CRC seed signatures.
- Tracks SQ availability and completion metadata through helpers from `mlx5_priv.h`.

Dependencies:
- `mlx5_priv.h`, `mlx5_ifc.h`, libibverbs/mlx5dv devx, SPDK mempool/thread/tree/log/util/RDMA helpers.

Important APIs:
- `spdk_mlx5_mkey_pool_init`, `spdk_mlx5_mkey_pool_destroy`
- `spdk_mlx5_mkey_pool_get_ref`, `spdk_mlx5_mkey_pool_put_ref`
- `spdk_mlx5_mkey_pool_get_bulk`, `spdk_mlx5_mkey_pool_put_bulk`
- `spdk_mlx5_umr_configure`, `spdk_mlx5_umr_configure_crypto`, `spdk_mlx5_umr_configure_sig`
- `spdk_mlx5_create_psv`, `spdk_mlx5_destroy_psv`, `spdk_mlx5_qp_set_psv`
- `spdk_mlx5_umr_implementer_register`, `spdk_mlx5_umr_implementer_is_registered`

Research notes:
- UMR WQE layout is explicitly documented in comments and aligned to 64-byte WQEBBs.
- Crypto supports AES-XTS-oriented BSF configuration and little/big endian simple LBA tweak modes.
- Signature support is CRC32C-focused and accepts seeds `0` or `0xffffffff`.
- Potential issue to verify: zero pool flags appear valid by mask checking, but `g_mkey_pool_names[0]` is unset and used in pool-name formatting.
