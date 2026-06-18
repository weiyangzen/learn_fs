# File Research: sources/local-fs/xfsprogs/libxfs/xfs_exchmaps.c

## Purpose
Implements XFS file mapping exchange support: estimating exchange cost, preparing deferred exchange intents, swapping extents between two inodes/forks, maintaining quota/reflink/extent-count state, and performing post-operation conversions back to shortform metadata when possible.

## Main Entry Points
- `xfs_exchmaps_check_forks()` rejects missing or local-format forks.
- `xfs_exchmaps_estimate()` walks mappings to estimate exchanged block counts, exchange count, extent-count deltas, and reservation overhead.
- `xfs_exchmaps_estimate_overhead()` adds bmbt/rmapbt reservation estimates.
- `xfs_exchmaps_intent_init_cache()` and `xfs_exchmaps_intent_destroy_cache()` manage the intent slab cache.
- `xfs_exchmaps_init_intent()` builds an in-core deferred intent from a request.
- `xfs_exchmaps_finish_one()` performs one deferred exchange step or post-operation cleanup and returns `-EAGAIN` when more transactions are needed.
- `xfs_exchmaps_ensure_reflink()` and `xfs_exchmaps_upgrade_extent_counts()` prepare inode flags before exchange work starts.
- `xfs_exchange_mappings()` schedules the deferred mapping exchange.

## Internal Mechanics
The exchange walker reads aligned mapping pairs from both inodes, skips file1 holes/unwritten extents when `XFS_EXCHMAPS_INO1_WRITTEN` allows it, handles realtime allocation-unit alignment, and rejects impossible delalloc or mismatched lookup results. A single exchange step unmaps both records, swaps logical offsets, maps each physical record into the other inode, updates quotas, and advances the intent cursor.

The estimator simulates the same walk, tracks adjacent mappings to estimate extent-count growth or shrinkage, records moved data/rt blocks, counts exchange steps, checks extent-counter overflow, and adds bmbt/rmapbt reservation overhead. Post-operation cleanup can convert inode2 attr/dir/symlink forks back to shortform and clear reflink flags when a full-file exchange allows the reflink state to be effectively swapped.

## Dependencies
Uses bmap read/map/unmap helpers, deferred operation plumbing, quota accounting, reflink/COW fork state, large extent count feature flags, dir/attr/symlink shortform conversion helpers, transaction logging, tracepoints, rmap/bmbt reservation constants, and `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`.

## Risks and Notes
This code assumes callers have flushed delalloc/pagecache state and hold both inode ILOCKs. Reservation estimation is conservative but complex, especially around mapping merge simulation and realtime unwritten extents. In `xfs_exchmaps_estimate_overhead()`, the final `UINT_MAX` check compares `req->resblks` before assigning the accumulated `resblks`, which is worth reviewing because overflow checks update the local variable first. Post-operation shortform conversion helpers can return without releasing buffers when conversion is not possible; that may be transaction-buffer ownership by convention, but it is a path to audit carefully.
