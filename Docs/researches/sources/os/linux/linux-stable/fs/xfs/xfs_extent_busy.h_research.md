# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_extent_busy.h

## Purpose

Declares busy extent data structures and APIs used by allocation and transaction code.

## Main Types

- `struct xfs_extent_busy`
  - rbtree node
  - transaction/discard list node
  - owning group
  - start block, length, flags
- `struct xfs_busy_extents`
  - list of related busy extents
  - endio work item
  - owner pointer for completion cleanup

## Main Flags

- `XFS_EXTENT_BUSY_DISCARDED`: extent is undergoing discard.
- `XFS_EXTENT_BUSY_SKIP_DISCARD`: do not discard this extent.

## Main API

- Insert, clear, search, reuse, and trim busy extents.
- Force/wait for busy extent progress.
- Wait for all busy extents in a mount.
- Test if a group busy list is empty and sample generation.
- Allocate a busy extent tree.
- Sort busy extent lists by group and block.

## Important Invariant

`xfs_group_has_extent_busy` disables busy tracking for zoned rtgroups because zone reset only occurs after transactions touching that zone are forced out.

## Research Notes

This header defines the contract between deferred free/log code and allocators: frees become busy extents until commit/discard state proves them reusable.
