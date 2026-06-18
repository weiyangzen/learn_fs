# File Research: sources/os/linux/linux-stable/fs/btrfs/delalloc-space.h

This header declares the delayed allocation reservation API used by Btrfs write, direct I/O, extent, and cleanup paths.

Exported API groups:
- Data reservation:
  - `btrfs_alloc_data_chunk_ondemand()`
  - `btrfs_check_data_free_space()`
  - `btrfs_free_reserved_data_space()`
  - `btrfs_free_reserved_data_space_noquota()`
- Combined delalloc reservation:
  - `btrfs_delalloc_reserve_space()`
  - `btrfs_delalloc_release_space()`
- Metadata-only reservation:
  - `btrfs_delalloc_reserve_metadata()`
  - `btrfs_delalloc_release_metadata()`
- Outstanding extent accounting:
  - `btrfs_delalloc_release_extents()`
  - `btrfs_delalloc_shrink_extents()`

Types are forward-declared to keep the interface light:
- `struct extent_changeset`
- `struct btrfs_inode`
- `struct btrfs_fs_info`

Role in Btrfs:
The header exposes the public reservation contract for code that dirties data or creates ordered extents. Callers must pair reserve and release functions carefully, especially when qgroup changesets are involved.
