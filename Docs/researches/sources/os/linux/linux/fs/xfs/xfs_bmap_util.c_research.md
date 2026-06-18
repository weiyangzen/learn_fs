# File Research: sources/os/linux/linux/fs/xfs/xfs_bmap_util.c

Provides higher-level bmap utilities for block mapping reports, preallocation, hole punching, EOF block trimming, collapse/insert range, and legacy extent swapping.

Key elements:
- `xfs_fsb_to_db` maps filesystem blocks to disk addresses, with realtime handling.
- `xfs_zero_extent` issues block zeroing for an inode extent.
- `xfs_bmap_count_leaves` and `xfs_bmap_count_blocks` count real extents and btree blocks, excluding delayed allocation.
- `xfs_getbmap` implements getbmapx reporting for data/attr/debug COW forks, flushing delalloc when needed, reporting holes, delalloc, unwritten/prealloc, and shared extent state.
- `xfs_bmap_punch_delalloc_range` removes delayed allocation extents from a byte range, with special zoned allocation-context accounting.
- `xfs_can_free_eofblocks` decides whether post-EOF real/delalloc blocks can be freed.
- `xfs_free_eofblocks` attaches quotas, waits for DIO, punches prealloc/delalloc or truncates post-EOF data extents transactionally.
- `xfs_alloc_file_space` implements preallocation, including extsize rounding, realtime/data reservations, repeated `xfs_bmapi_write`, and `XFS_DIFLAG_PREALLOC`.
- `xfs_flush_unmap_range` writes back and invalidates the page cache around extent-aligned modification ranges.
- `xfs_free_file_space` punches complete blocks, handles big realtime allocation-unit alignment, and zeroes partial block edges without extending EOF.
- `xfs_prepare_shift` frees EOF blocks, flushes/invalidate ranges, and cancels COW data before extent shifts.
- `xfs_collapse_file_space` frees a range then shifts later extents left.
- `xfs_insert_file_space` verifies insertability, splits at the insertion point, and shifts extents right.
- `xfs_swap_extents_check_format` validates data fork formats and quota identity before swap.
- `xfs_swap_extent_flush` flushes and invalidates page cache for swap participants.
- `xfs_swap_extent_rmap` remaps extents one piece at a time when rmapbt is enabled.
- `xfs_swap_extent_forks` swaps data forks directly when rmapbt is absent, adjusts block counts/delalloc accounting, and sets inode log flags.
- `xfs_swap_change_owner` fixes bmbt block owner fields after fork swaps on v3 inode filesystems.
- `xfs_swap_extents` performs the legacy full-file swap operation with locking, quota attach, format checks, timestamp validation, reflink/COW handling, rmap or fork-swap logic, and transaction commit.

Dependencies:
- Uses XFS bmap core, transactions, quotas, reflink, iomap-adjacent flushing, realtime allocation geometry, zoned allocation context, and rmap/refcount-aware remap logic.

Research notes:
- getbmap reports shared/unshared subranges separately by trimming around reflink sharing.
- Collapse/insert range must stabilize page cache and COW fork state to avoid extent-shift races.
- `xfs_swap_extents` is full-file only and rejects realtime-group files because the deprecated interface cannot recover such swaps after crash.
- Fork swapping without rmapbt requires careful bmbt owner relogging for crash recovery.
- Preallocated files keep speculative real preallocations during EOF cleanup unless delayed allocations must be removed.
