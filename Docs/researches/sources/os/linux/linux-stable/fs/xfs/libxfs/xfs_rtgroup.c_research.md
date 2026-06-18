# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtgroup.c

## Purpose

Implements in-core realtime group management for XFS, including realtime group geometry, metadata inode lifecycle, locking and transaction joining, realtime superblock verification, and realtime superblock logging.

## Main Responsibilities

- Computes per-rtgroup geometry:
  - `xfs_rtgroup_extents`
  - `xfs_rtgroup_calc_geometry`
  - `xfs_update_last_rtgroup_size`
- Allocates and frees in-core `struct xfs_rtgroup` objects:
  - `xfs_rtgroup_alloc`
  - `xfs_rtgroup_free`
  - `xfs_initialize_rtgroups`
  - `xfs_free_rtgroups`
- Locks per-rtgroup metadata inodes:
  - bitmap and summary inodes for non-zoned realtime
  - rmap inode when rtrmapbt exists
  - refcount inode when rtreflink exists
- Loads and creates rtgroup metadata inodes under the metadata directory.
- Verifies and updates realtime superblock buffers via `xfs_rtsb_buf_ops`.

## Key Data Flow

`xfs_rtginode_ops` maps each rtgroup metadata inode type to:
- short name
- metafile type
- sickness flag
- valid data fork formats
- feature predicate
- create callback

This table drives loading, creation, validation, and health reporting for:
- realtime bitmap
- realtime summary
- realtime rmap btree
- realtime refcount btree

## Important Invariants

- Rtgroup zero can reserve its first realtime extent for the realtime superblock when `xfs_has_rtsb(mp)`.
- Non-rtgroups filesystems only load classic global realtime bitmap and summary inodes.
- Rtgroup metadata inode `i_projid` must equal the realtime group number.
- Metadata inode fork format must match the expected feature:
  - bitmap/summary: extents or btree
  - rmap/refcount: metadata btree
- Zoned realtime filesystems skip bitmap and summary locking because free-space management differs.

## Dependencies

- Uses generic group infrastructure through `xfs_group_*`.
- Uses metadata directory helpers for rtgroup inode paths and creation.
- Uses `xfs_rtrmapbt_create` and `xfs_rtrefcountbt_create` for btree metafiles.
- Uses `xfs_rtbitmap_create` and `xfs_rtsummary_create` for bitmap metadata.
- Exports `xfs_rtsb_buf_ops`, referenced through shared verifier declarations.

## Research Notes

This file is the central coordinator for the new rtgroups model. It bridges generic group lifecycle, metadata directory layout, realtime bitmap metadata, rmap/refcount btrees, and the realtime superblock. Most callers should use the helper lock/join APIs instead of locking rtgroup metadata inodes directly.
