# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_zones.h

## Purpose

Declares zoned realtime validation and defines zoned allocator/GC reservation constants.

## Main Constants

- `XFS_GC_ZONES`
  - reserves zones for garbage collection progress.
- `XFS_RESERVED_ZONES`
  - GC reserve plus user-write reserve.
- `XFS_MIN_ZONES`
  - minimum total zones needed.
- `XFS_OPEN_GC_ZONES`
  - open-zone reserve for GC.
- `XFS_MIN_OPEN_ZONES`
  - minimum open-zone limit.
- `XFS_DEFAULT_MAX_OPEN_ZONES`
  - default open-zone cap when hardware does not provide one.

## Main API

- `xfs_validate_blk_zone`

## Research Notes

The constants encode forward-progress guarantees for zoned realtime allocation and garbage collection.
