# File Research: sources/local-fs/kdave-linux/fs/btrfs/delalloc-space.h

This header exposes the delalloc data and metadata reservation API implemented by `delalloc-space.c`.

Declared API groups:
- Data reservation:
  - `btrfs_alloc_data_chunk_ondemand()`
  - `btrfs_check_data_free_space()`
  - `btrfs_free_reserved_data_space()`
  - `btrfs_free_reserved_data_space_noquota()`
- Combined delalloc reservation:
  - `btrfs_delalloc_reserve_space()`
  - `btrfs_delalloc_release_space()`
- Metadata reservation:
  - `btrfs_delalloc_reserve_metadata()`
  - `btrfs_delalloc_release_metadata()`
  - `btrfs_delalloc_release_extents()`
  - `btrfs_delalloc_shrink_extents()`

Design notes:
- Forward declares `extent_changeset`, `btrfs_inode`, and `btrfs_fs_info`.
- The API makes qgroup range tracking explicit through `struct extent_changeset **reserved` on reservation and `struct extent_changeset *reserved` on release.
- `btrfs_delalloc_reserve_metadata()` accepts separate logical and disk byte counts, which matters for compressed or otherwise transformed writes.
