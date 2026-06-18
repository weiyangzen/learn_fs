# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_types.c

## Purpose

Implements type and range validators for XFS block numbers, inode numbers, realtime block numbers, inode counts, directory/attribute block offsets, and file offsets.

## Main Functions

- Data block validation:
  - `xfs_verify_fsbno`
  - `xfs_verify_fsbext`
- Inode validation:
  - `xfs_verify_ino`
  - `xfs_is_sb_inum`
  - `xfs_verify_dir_ino`
  - `xfs_icount_range`
  - `xfs_verify_icount`
- Realtime block validation:
  - `xfs_verify_rtbno`
  - `xfs_verify_rtbext`
- Offset validation:
  - `xfs_verify_dablk`
  - `xfs_verify_fileoff`
  - `xfs_verify_fileext`

## Important Invariants

- Data filesystem block numbers must:
  - lie within an AG
  - not point at static AG metadata
  - not cross AG boundaries for extents
- Directory inode numbers must not point to internal superblock inodes or quota inodes.
- Realtime block validation changes when rtgroups are enabled:
  - group number must be valid
  - realtime extent index must fit within that group
  - rtgroup zero realtime superblock extent is not allocatable
  - extents must not cross rtgroup boundaries
- File and extent range checks reject wraparound.

## Dependencies

- Uses AG geometry helpers.
- Uses rtgroup conversion helpers.
- Uses realtime extent conversion helpers from the realtime bitmap layer.

## Research Notes

This file centralizes low-level validation used throughout libxfs. The rtgroup-aware realtime block validation is the main recent feature integration point.
