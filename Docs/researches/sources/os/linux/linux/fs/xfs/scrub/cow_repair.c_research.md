# File Research: sources/os/linux/linux/fs/xfs/scrub/cow_repair.c

## Role
Repairs an inode's in-core CoW fork mappings. Since CoW staging extents are represented ondisk by refcount/rmap metadata rather than durable per-inode ownership, repair replaces only bad unwritten CoW fork mappings and reaps discarded staging blocks.

## Main Data Structures
- `struct xrep_cow`: repair context containing bad file-offset bitmap, old-block bitmap for data or realtime blocks, current CoW fork record, and scanning cursors.
- `struct xrep_cow_extent`: replacement physical extent descriptor.

## Detection Flow
- Iterates CoW fork extents in `xrep_bmap_cow`.
- Skips delalloc mappings because they are incore only.
- Skips written CoW extents because they may already be under writeback and cannot be relocated safely.
- For data device mappings, `xrep_cow_find_bad` checks refcount and rmap btrees in the containing AG.
- For realtime mappings, `xrep_cow_find_bad_rt` performs analogous checks with rtgroup rmap/refcount cursors.
- Marks file ranges bad if they are shared, missing CoW staging refcount records, cross-linked by rmap records not owned by `XFS_RMAP_OWN_COW`, or forced by rebuild/debug flags.

## Repair Flow
- `xoff_bitmap_walk` calls `xrep_cow_replace` for each bad file-offset range.
- `xrep_cow_replace_range` finds the current mapping, allocates replacement CoW staging space on the data or realtime device, updates the incore CoW fork, finishes deferred metadata work, and records old physical blocks for reaping.
- `xrep_cow_replace_mapping` updates or splits the existing CoW fork extent so the replacement covers the beginning of the bad range.
- Old staging blocks are reaped with `xrep_reap_fsblocks` or `xrep_reap_rtblocks` using CoW owner info.

## Preconditions and Limits
- Requires both rmapbt and reflink.
- Does nothing if the inode has no CoW fork.
- Rejects realtime inodes with large realtime allocation units and realtime metadata inodes.
- If the CoW fork is not in extents format, it is reinitialized to an empty extent fork.

## Invariants
- Replacement length is capped to `XFS_MAX_BMBT_EXTLEN` and to one current CoW fork record at a time.
- Allocated replacement extents are immediately recorded as CoW staging extents in refcount metadata.
- Mapping changes happen while the inode fork is stable under scrub/repair locking.
