# File Research: sources/os/linux/linux/fs/xfs/scrub/scrub.h

This header defines the core online scrub context, operation dispatch contracts, scheduler-relaxation helpers, state flags, subordinate scrub support, and scrub/xref function declarations used throughout `fs/xfs/scrub`.

Key types:
- `struct xchk_relax`: rate-limited scheduler yielding and fatal signal polling state.
- `struct xchk_meta_ops`: setup/scrub/repair/repair_eval/feature-test callbacks plus operation selector type.
- `struct xchk_ag`: per-AG buffers and btree cursors.
- `struct xchk_rt`: realtime group lock state and rt btree cursors.
- `struct xfs_scrub`: central per-operation state object.
- `struct xfs_scrub_subord`: subordinate scrub context used by repair routines.

Important helpers/macros:
- `INIT_XCHK_RELAX`: initializes yielding state.
- `xchk_maybe_relax`: amortizes `cond_resched` and fatal-signal checks.
- `XCHK_GFP_FLAGS`: scrub allocation policy with no warnings and retry-mayfail behavior.
- `XCHK_IGET_FLAGS`: untrusted, donotcache inode lookup flags for fsck operations.
- `xchk_should_terminate`: standard interruption check.
- `xchk_nothing`: disabled scrubber placeholder returning `-ENOENT`.

State flags:
- `XCHK_TRY_HARDER`: retry after resource/lock-order limits.
- `XCHK_HAVE_FREEZE_PROT`: mount write protection held.
- `XCHK_FSGATES_*`: dynamic hook/fsgate state for drain/quota/dirent/rmap live updates.
- `XCHK_NEED_DRAIN`: retry setup after defer-op drain requirement.
- `XREP_RESET_PERAG_RESV`: repair must reset AG reservation.
- `XREP_ALREADY_FIXED`: repair already ran and current pass is evaluating it.

Declared scrubbers:
- Metadata scrubbers for AG headers, allocation/inode/rmap/refcount btrees, inode/forks, directory, xattr, symlink, parent pointers, dirtree, metapath, quotas, filesystem counters, nlinks, and realtime metadata.
- Realtime and quota declarations compile to `xchk_nothing` stubs when config options are off.

Declared cross-reference helpers:
- Data-device helpers check ownership, free/used state, inode chunks, CoW staging, and shared extents.
- Realtime helpers mirror ownership/shared/CoW checks for rt space and compile to no-ops without `CONFIG_XFS_RT`.

Risk notes:
- `xfs_scrub` owns many resource lifetimes, including transactions, inode locks, tempfiles, orphanage state, xfiles, and per-AG/per-rtgroup cursors; teardown ordering is critical.
- `xchk_maybe_relax` only checks expensive conditions every 100 calls and yields at most 10 times per second.
