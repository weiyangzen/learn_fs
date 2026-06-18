# File Research: sources/os/linux/linux/fs/btrfs/delalloc-space.h

This header exposes the delayed allocation reservation API implemented by `delalloc-space.c`.

Exported API groups:
- Data reservation: `btrfs_alloc_data_chunk_ondemand()`, `btrfs_check_data_free_space()`, `btrfs_free_reserved_data_space()`, and `btrfs_free_reserved_data_space_noquota()`.
- Combined delalloc data and metadata reservation: `btrfs_delalloc_reserve_space()` and `btrfs_delalloc_release_space()`.
- Metadata reservation lifecycle: `btrfs_delalloc_reserve_metadata()`, `btrfs_delalloc_release_metadata()`, `btrfs_delalloc_release_extents()`, and `btrfs_delalloc_shrink_extents()`.

Design notes:
- The header forward declares the small set of Btrfs and extent state types needed by callers.
- Qgroup range tracking is explicit: callers pass `struct extent_changeset **reserved` when reserving and the resulting `struct extent_changeset *reserved` when releasing.
- `btrfs_delalloc_reserve_metadata()` accepts logical and disk byte counts separately, which matters for callers whose on-disk size may differ from the dirty logical range.
