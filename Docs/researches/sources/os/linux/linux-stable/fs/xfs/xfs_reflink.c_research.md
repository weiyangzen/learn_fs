# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_reflink.c

## Purpose
Implements XFS reflink and copy-on-write behavior: shared extent detection, CoW fork allocation/conversion/cancellation, CoW completion remapping, leftover CoW recovery, range clone/remap, unshare, reflink flag maintenance, and realtime reflink constraints.

## Main APIs
- `xfs_reflink_trim_around_shared` and `xfs_bmap_trim_cow` split file mappings at shared/unshared boundaries.
- `xfs_reflink_allocate_cow` allocates or reuses CoW fork staging blocks for writes to shared extents.
- `xfs_reflink_convert_cow` and `xfs_reflink_convert_cow_locked` convert unwritten CoW extents to written extents.
- `xfs_reflink_cancel_cow_blocks` and `xfs_reflink_cancel_cow_range` remove CoW fork reservations or real staging extents.
- `xfs_reflink_end_cow` and `xfs_reflink_end_atomic_cow` remap completed CoW data into the data fork.
- `xfs_reflink_recover_cow` frees orphaned CoW staging extents from refcount metadata during recovery.
- `xfs_reflink_remap_prep`, `xfs_reflink_remap_blocks`, and `xfs_reflink_update_dest` implement range cloning.
- `xfs_reflink_inode_has_shared_extents`, `xfs_reflink_clear_inode_flag`, and `xfs_reflink_unshare` maintain or remove the inode reflink flag.

## Key Behavior
Shared extent detection queries data-device refcount btrees or realtime refcount btrees and returns the first shared run inside a mapping. Write paths use this to trim mappings so unshared and shared regions can be processed separately. Always-CoW inodes force real extents to be treated as shared.

CoW allocation first checks for an existing overlapping CoW fork mapping. It reuses real or delalloc CoW fork extents when possible, otherwise allocates unwritten staging extents using write transactions and the inode’s CoW extent size hint. Direct I/O can request immediate conversion to written extents; buffered writes leave staging extents unwritten until writeback.

CoW cancellation walks the CoW fork backwards over a range, deletes delayed reservations, frees unwritten or requested real staging extents, removes CoW orphan records, frees physical blocks, rolls transactions through deferred work, unreserves quota, and clears the cowblocks tag when the fork is empty.

CoW completion unmaps the old data fork extent, decrements its refcount, removes delalloc reservations if present, frees the CoW orphan record, maps the written CoW extent into the data fork, adjusts quota from delayed to real blocks, deletes the CoW fork mapping, and advances through the completed I/O range. Atomic CoW reserves enough btree split space to remap the full range in one transaction.

Range clone preparation locks both files against I/O and mmap faults, rejects incompatible realtime/DAX combinations, runs generic or DAX remap prep, attaches destination dquots, zeros destination post-EOF preallocation gaps, sets reflink flags, flushes/unmaps destination cache, and leaves locks arranged for remap. Remap loops source extents, rejects unexpected delalloc, unmaps destination extents, increments source block refcounts, maps written source extents into destination, updates destination size, and reports partial progress.

Reflink flag clearing scans all written data fork extents for shared blocks and cancels leftover CoW blocks before clearing the inode flag. Unshare drives iomap or DAX writeback over a range, waits for writeback, then attempts to clear the reflink flag.

## Dependencies
Uses XFS bmap, refcount, realtime refcount, transaction, quota, iomap, DAX, page cache, inode locking, AG/rtgroup metadata, btree cursor, free-space reservation, health marking, and generic remap helpers.

## Failure Handling
Detects and marks data fork corruption for impossible same-block/different-state mappings or unexpected delalloc source extents. Low rmapbt/metafile reservations can reject reflink with `-ENOSPC`. Realtime reflink requires rtgroups and realtime extent size of one filesystem block.
