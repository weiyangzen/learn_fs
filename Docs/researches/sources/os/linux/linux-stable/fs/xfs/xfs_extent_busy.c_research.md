# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_extent_busy.c

## Purpose

Tracks extents that have been freed in memory but cannot yet be safely reused because the freeing transaction has not reached stable log state or discard processing is still active.

## Main Responsibilities

- Maintains per-group busy extent rbtrees through `struct xfs_extent_busy_tree`.
- Inserts busy extents from transaction and discard paths:
  - `xfs_extent_busy_insert`
  - `xfs_extent_busy_insert_discard`
- Searches for exact or partial overlaps:
  - `xfs_extent_busy_search`
- Allows safe reuse of non-userdata busy extents when the busy extent can be removed or shortened without splitting immutable transaction/CIL lists.
- Trims candidate allocation extents away from busy ranges through `xfs_extent_busy_trim`.
- Clears busy extents after commit/discard:
  - `xfs_extent_busy_clear`
  - `xfs_extent_busy_clear_one`
- Forces and waits for log progress when allocation conflicts with busy extents:
  - `xfs_extent_busy_flush`
  - `xfs_extent_busy_wait_all`
- Sorts busy extents by group and block for processing.
- Allocates and initializes busy extent trees.

## Important Invariants

- Busy extents in the rbtree must not overlap.
- Busy list membership is tied to transaction/CIL context and cannot be arbitrarily split.
- Fully consumed busy extents are removed from the rbtree and marked invalid by setting length to zero, but list cleanup happens later.
- User allocations cannot reuse overlapping busy extents; the log must be forced and allocation retried.
- Extents undergoing discard are marked `XFS_EXTENT_BUSY_DISCARDED` and require retry.
- Zoned realtime groups do not need busy extent tracking because zone reset ordering handles safe freeing.

## Dependencies

- Operates on generic `struct xfs_group`, so it supports AGs and non-zoned rtgroups.
- Uses log forcing for busy resolution.
- Uses waitqueue generation counters to wait for progress without assuming the busy tree is empty after wakeup.
- Iterates AGs and rtgroups for wait-all behavior.

## Research Notes

This file is a core allocator safety mechanism. It prevents stale metadata/data exposure by ensuring blocks freed by uncommitted transactions are not reused too early, while still allowing carefully constrained reuse for metadata allocations under low-space pressure.
