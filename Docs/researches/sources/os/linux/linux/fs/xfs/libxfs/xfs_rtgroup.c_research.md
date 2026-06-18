# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtgroup.c

## Purpose

`xfs_rtgroup.c` implements in-core realtime group management for XFS. It handles realtime group geometry, lifecycle, metadata inode locking/loading/creation, realtime group geometry reporting, and realtime superblock verification/logging.

## Main Content

- Computes per-realtime-group geometry:
  - Handles the first usable block, including reservation of the first realtime extent for an RT superblock when present.
  - Computes extents in each group, including shorter tail groups.
  - Precomputes group block count and minimum usable group block.
- Allocates, inserts, frees, and initializes `struct xfs_rtgroup` objects through the generic `xfs_group` infrastructure.
- Updates the previous last realtime group size after growfs recovery changes realtime geometry.
- Provides RT group metadata inode locking:
  - Bitmap and summary locks for non-zoned realtime devices.
  - Rmap and refcount metadata inode locks when present.
  - Transaction join helper for locked RT metadata inodes.
- Reports RT group geometry and health through `struct xfs_rtgroup_geometry`.
- Defines RT group metadata inode operations for bitmap, summary, rmap, and refcount inodes:
  - Feature predicates.
  - Metadata inode type.
  - Valid data fork formats.
  - Sickness bits.
  - Creation callbacks.
- Loads metadata inodes from legacy superblock inode fields or from the metadata directory `rtgroups/<rgno>.<name>` paths.
- Creates metadata directory entries and initializes metadata inodes.
- Provides lockdep ordering support for RT group metadata inode locks.
- Verifies, reads, writes, and logs realtime superblocks (`xfs_rtsb_buf_ops`, `xfs_update_rtsb`, `xfs_log_rtsb`).

## Key Interfaces and Invariants

- RT group zero can reserve the first realtime extent for the realtime superblock.
- `xfs_initialize_rtgroups` unwinds all newly inserted groups if any allocation fails.
- `xfs_update_last_rtgroup_size` requires an active reference to the old tail RT group.
- `XFS_RTGLOCK_BITMAP` and `XFS_RTGLOCK_BITMAP_SHARED` are mutually exclusive.
- Zoned realtime devices do not use bitmap/summary inode locking through this path.
- Metadata inode format is validated against the expected format mask for each inode type.
- Metadata inode project id must equal the RT group number.
- Missing or corrupt metadata directory state marks the filesystem metadir sick.
- RT superblocks must match the filesystem label, UUID, and metadata UUID and must have zero padding.

## Dependencies

Depends on generic group management, metadata directory APIs, transaction/inode APIs, realtime bitmap/summary creation, realtime rmap/refcount btree creation, health tracking, buffer verifiers, and superblock feature predicates.
