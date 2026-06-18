# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_recovery.c

Implements dirty-shutdown recovery for SPDK FTL. The public entry point `ftl_mngt_recover()` runs `g_desc_recovery`, a management-process pipeline that restores band state, P2L checkpoints, NV cache state, trim state, L2P, valid maps, core poller, optional self-test, and final startup.

Important control flow:
- `ftl_mngt_recovery_init()` computes DRAM-bounded L2P snippet size from `l2p_dram_limit`, unlinks stale L2P cache SHM, allocates temporary recovery metadata, and initializes iteration ranges.
- `g_desc_recovery_iteration` reconstructs one L2P slice by loading persisted L2P, initializing seq IDs from trim metadata, replaying NV cache chunk P2L, replaying band P2L, rebuilding valid bits, then persisting the slice.
- Band replay reads tail metadata, validates closed-band P2L CRC, resolves newer sequence IDs, and invalidates stale overlapping P2L entries on open/full bands.
- NV cache replay validates chunk P2L CRC and wins L2P conflicts by sequence ID.
- Trim recovery has normal and shared-memory paths; it can complete in-progress trim metadata from SHM or recover a logged trim transaction from `TRIM_LOG`.

Key dependencies:
- Management process API from `ftl_mngt`.
- Metadata IO from `ftl_md`.
- Band/P2L checkpoint functions from band and P2L modules.
- `ftl_addr_utils.h` for packed/unpacked address load/store.

Notable risks and invariants:
- Checkpoint recovery is explicitly unsupported in `ftl_mngt_recovery_iteration_init_seq_ids()` when `ckpt_seq_id` is nonzero.
- Recovery assumes P2L CRCs and seq IDs are authoritative for conflict resolution.
- Duplicate valid-map hits assert and fail recovery, which is appropriate for metadata corruption.
- Open-band recovery depends on P2L checkpoint region availability and temporarily requeues bands through `shut_bands`.
