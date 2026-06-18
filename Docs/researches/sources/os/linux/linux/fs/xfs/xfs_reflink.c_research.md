# File Research: sources/os/linux/linux/fs/xfs/xfs_reflink.c

## Role

XFS reflink and copy-on-write implementation. It coordinates shared extent detection, CoW fork allocation/conversion/cancelation, IO completion remapping, range clone/remap, unshare, and reflink flag maintenance.

## Main Responsibilities

- Detects shared data or realtime extents via refcount btrees with `xfs_reflink_find_shared` and `xfs_reflink_find_rtshared`.
- Trims mappings around shared/unshared boundaries with `xfs_reflink_trim_around_shared` and `xfs_bmap_trim_cow`.
- Allocates or reuses CoW fork staging extents in `xfs_reflink_allocate_cow`, including delayed allocation conversion.
- Converts unwritten CoW fork extents to real extents before IO through `xfs_reflink_convert_cow_locked` and `xfs_reflink_convert_cow`.
- Cancels CoW reservations and frees orphan CoW extents with `xfs_reflink_cancel_cow_blocks` and `xfs_reflink_cancel_cow_range`.
- Completes CoW IO by remapping written CoW fork extents into the data fork using `xfs_reflink_end_cow` or one-transaction atomic mode `xfs_reflink_end_atomic_cow`.
- Computes maximum software atomic CoW size through `xfs_reflink_max_atomic_cow`.
- Recovers leftover CoW staging extents at mount with `xfs_reflink_recover_cow`.
- Implements file range remapping through `xfs_reflink_remap_prep`, `xfs_reflink_remap_blocks`, `xfs_reflink_remap_extent`, and `xfs_reflink_update_dest`.
- Maintains inode reflink flags and CoW fork state through `xfs_reflink_set_inode_flag`, `xfs_reflink_inode_has_shared_extents`, `xfs_reflink_clear_inode_flag`, and `xfs_reflink_unshare`.
- Validates realtime reflink support with `xfs_reflink_supports_rextsize`.

## Important Invariants

- Shared written blocks are never overwritten in place; writes allocate staging blocks in the CoW fork and remap after IO succeeds.
- CoW fork preallocation can be larger than the IO range due to `cowextsize`; remap completion only moves written real extents.
- Data and realtime file ranges cannot be reflinked to each other.
- DAX and non-DAX files cannot share data.
- Dedupe/clone handling rejects or trims partial EOF block cases that could expose stale data.
- Reflink on realtime requires rtgroups and realtime extent size of one filesystem block.
- Quota updates distinguish CoW delayed/reserved counts from real data or realtime block counts.

## Locking and Transactions

Range remap preparation takes IO and mmap locks on both files. CoW completion uses one transaction per remapped extent for normal IO and one larger transaction for atomic CoW. Destination remap transactions reserve bmbt and quota space conservatively, then refine after reading the existing destination mapping.

## Dependencies

Uses bmap, refcount, rmap-related reservations, quota, iomap, DAX, transactions, AG reservation, realtime groups/refcount btrees, metadir reservation, and inode/pagecache synchronization.
