# File Research: sources/os/linux/linux/fs/xfs/xfs_extent_busy.h

Declares busy-extent structures and APIs.

Key contents:
- `struct xfs_extent_busy`: rb-tree node, list node, owning group, group-relative block range, and flags.
- Flags:
  - `XFS_EXTENT_BUSY_DISCARDED`: discard operation in progress.
  - `XFS_EXTENT_BUSY_SKIP_DISCARD`: do not discard.
- `struct xfs_busy_extents`: list plus work item and owner pointer for tracking discard completion batches.
- APIs for insertion, discard insertion, clearing, searching, reuse, trimming, flushing, global waiting, empty query, tree allocation, and sorting.
- `xfs_group_has_extent_busy` notes that zoned realtime groups skip busy extent tracking because zone reset orders transactions first.

This header defines the allocator/log interface for preventing premature reuse of recently freed blocks.
