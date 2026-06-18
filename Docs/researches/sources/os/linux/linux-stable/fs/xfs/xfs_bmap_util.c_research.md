# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_util.c

## Purpose

Provides kernel-only bmap utility operations for block address conversion, extent counting, `getbmap`, delayed-allocation cleanup, EOF block freeing, fallocate-style space changes, and whole-file extent swapping.

## Main Responsibilities

- Converts XFS filesystem blocks to disk addresses, including realtime inodes.
- Issues zeroout for allocated extents.
- Counts extent records and btree blocks in inode forks.
- Implements `xfs_getbmap` reporting.
- Punches delayed-allocation extents from ranges.
- Determines and frees post-EOF blocks.
- Allocates preallocated file space.
- Frees file space and zeroes partial boundary blocks.
- Prepares and performs collapse/insert range operations.
- Swaps extents between a target inode and temporary inode for defragmentation.

## getbmap Behavior

`xfs_getbmap` validates flags, chooses data/attr/COW fork, flushes delalloc when required, reads extents, reports holes unless suppressed, reports delalloc/prealloc/shared flags, and splits records around shared/unshared boundaries for accurate output.

## Space Manipulation

- `xfs_bmap_punch_delalloc_range` removes delalloc extents without transactions.
- `xfs_free_file_space` flushes and invalidates page cache, unmaps full blocks, and zeroes partial blocks without extending EOF.
- `xfs_collapse_file_space` frees the range, prepares shift state, then shifts extents left.
- `xfs_insert_file_space` verifies insert feasibility, splits at the insertion point, then shifts extents right.

## EOF Cleanup

`xfs_can_free_eofblocks` avoids expensive extent reads and skips inappropriate files. `xfs_free_eofblocks` frees post-EOF extents without updating on-disk file size, preserving crash behavior for dirty data.

## Extent Swap

`xfs_swap_extents`:
- locks both files and page-cache invalidation locks
- verifies file type, realtime status, quota ids, timestamps, and full-file swap parameters
- flushes both mappings
- cancels temporary inode COW data
- either swaps forks directly or remaps extents when rmapbt is enabled
- swaps reflink/COW state as needed
- fixes bmbt block owners for v3 inode btrees

## Important Invariants

- Shift operations flush, invalidate, and cancel COW state from the affected range to avoid offset corruption.
- Big realtime allocation files can only free complete realtime extents.
- Preallocated files keep real speculative preallocation unless only delayed allocations need cleanup.
- The legacy swapext interface does not support rtgroups.
- Fork format checks prevent swapping a data fork into an inode where it cannot fit.

## Dependencies

- Bmap, bmbt, allocation, realtime, quota, reflink, iomap, and transaction code.
- Page cache writeback/invalidation helpers.
- Rmap-aware remapping when reverse mapping btrees are enabled.

## Research Notes

This file is the high-level extent manipulation utility layer. The riskiest areas are page-cache synchronization before extent shifts, delayed allocation accounting, and fork-format compatibility during swapext.
