# File Research: sources/os/linux/linux/fs/xfs/xfs_zone_alloc.c

## Purpose

Implements the XFS zoned realtime allocator. It manages open zones, allocates write placement for zoned data I/O, maps completed writes into files, tracks reclaimable zones, and initializes zone state at mount.

## Main Responsibilities

- Maintains `struct xfs_open_zone` references and RCU freeing.
- Tracks free, open, GC, full, and reclaimable zones.
- Buckets reclaimable fully written zones by used-block percentage.
- Selects open zones based on write lifetime hints, LRU/MRU policy, and small-file packing.
- Opens new zones subject to open-zone and GC reserve limits.
- Allocates physical blocks from open zones for iomap writeback.
- Submits zone append or conventional write bios.
- Converts completed zoned writes into data fork mappings.
- Frees zoned blocks by decrementing per-zone rmap used counters.
- Reconstructs zone write pointers and open/free/reclaimable state at mount.
- Calculates open-zone limits and initializes/tears down zoned mount state.

## Important Invariants

- `oz_allocated` is protected by `oz_alloc_lock`.
- `oz_written` is protected by the realtime group rmap inode lock.
- `oz_written <= oz_allocated`.
- A full open zone is removed from open-zone accounting and may become reclaimable.
- Empty zones are marked `XFS_RTG_FREE`.
- Sequential zones use hardware write pointers; conventional zones infer the write pointer from rmap.
- Zoned filesystems require realtime groups, rmapbt, `rextsize == 1`, and a minimum zone count.
- Completed GC writes must not overwrite newer user writes; old startblock comparison detects races.

## Dependencies

Uses XFS realtime groups, rmap inodes, iomap ioends, bmap/refcount/free extent logic, free counters, zone validation, GC hooks, write hints, and block-device zone APIs.

## Research Notes

This is the core zoned XFS allocator. The most subtle paths are write completion remapping, open-zone reference caching in inodes, reclaimable accounting transitions, and mount-time recovery of zone state after power loss.
