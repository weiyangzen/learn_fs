# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/scrub.h

Defines core scrub state, dispatch contracts, scheduler-yield helpers, and scrubber prototypes.

Key structures:
- `struct xchk_relax` and `xchk_maybe_relax` rate-limit `cond_resched` and fatal-signal checks during long scans.
- `enum xchk_type` categorizes scrub inputs as disabled, per-AG, per-filesystem, per-inode, generic, or realtime-group metadata.
- `struct xchk_meta_ops` is the per-scrub-type operation table contract.
- `struct xchk_ag` stores per-AG buffers and btree cursors.
- `struct xchk_rt` stores realtime group state and realtime btree cursors.
- `struct xfs_scrub` is the central operation context, carrying mount, metadata request, transaction, target inode, temp inode, buffers, xfile/xmbuf state, lock flags, health masks, retry/gate flags, and AG/RT substate.
- `struct xfs_scrub_subord` snapshots state for nested scrub operations.

Important constants:
- `XCHK_GFP_FLAGS` standardizes scrub allocations as retryable/no-warning kernel allocations.
- `XCHK_IGET_FLAGS` marks scrub-by-handle inode lookups as untrusted and non-cache-polluting.
- `XCHK_TRY_HARDER`, `XCHK_NEED_DRAIN`, `XCHK_FSGATES_*`, and `XREP_*` flags encode retry, live-update gate, and repair state.

Exports:
- Declares all major scrub entrypoints for metadata, inode data, realtime metadata, quota checks, filesystem counters, nlinks, and cross-reference helpers.
- Provides no-op fallbacks when realtime or quota support is disabled.
