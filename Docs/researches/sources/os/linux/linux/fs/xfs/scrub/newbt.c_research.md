# File Research: sources/os/linux/linux/fs/xfs/scrub/newbt.c

Provides shared infrastructure for staging and bulk-loading replacement btrees during online repair. It reserves blocks, feeds them to btree bulk loaders, tracks unused reservation space, and commits or cancels reservations safely.

Main functions:
- `xrep_newbt_estimate_slack` chooses btree bulk-load slack, tightening trees when the AG or filesystem has less than about 10 percent free space, unless debug tunables override defaults.
- `xrep_newbt_init_ag` initializes new per-AG btree staging state with owner info, allocation hint, reservation type, reservation list, and bulk-load limits.
- `xrep_newbt_init_inode` initializes an inode-fork fake root for rebuilding file btrees.
- `xrep_newbt_init_metadir_inode` initializes metadata inode btree rebuild state using regular block allocation semantics until commit.
- `xrep_newbt_init_bare` initializes a minimal staging object for callers managing reservations manually.
- `xrep_newbt_add_blocks` creates a reservation record and, for transaction-backed allocations, schedules autoreap so uncommitted blocks can be freed.
- `xrep_newbt_add_extent` adds caller-supplied space to the reservation pool.
- `xrep_newbt_alloc_ag_blocks` and `xrep_newbt_alloc_file_blocks` allocate per-AG or file-based btree blocks, validate allocation hints, add reservations, and finish deferred ops as they go.
- `xrep_newbt_alloc_blocks` chooses AG or file allocation based on whether `sc->ip` is set.
- `xrep_newbt_free_extent` handles commit/cancel semantics for each reservation, freeing unused ranges with EFIs and autoreap handling.
- `xrep_newbt_free`, `xrep_newbt_commit`, and `xrep_newbt_cancel` clean reservation state after successful btree commit or aborted repair.
- `xrep_newbt_claim_block` hands one reserved block to the btree bulk loader, advances reservation usage, writes the correct short/long btree pointer, and relogs deferred frees.
- `xrep_newbt_unused_blocks` totals unconsumed reserved blocks.

Important behavior:
- Autoreap protects against block leaks if repair fails before commit.
- Unused committed reservation space is freed through deferred extent frees.
- The code periodically finishes deferred frees to avoid overlarge truncate-style EFI reservations.
