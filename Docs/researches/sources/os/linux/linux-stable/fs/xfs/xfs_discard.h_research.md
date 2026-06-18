# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_discard.h

## Purpose
Declares XFS discard/FITRIM entry points.

## API
- `xfs_discard_extents` issues discard I/O for busy extents.
- `xfs_ioc_trim` implements the FITRIM ioctl for an XFS mount and user `fstrim_range`.

## Dependencies
Forward-declares `fstrim_range`, `xfs_mount`, and `xfs_busy_extents`; implementation details live in `xfs_discard.c`.
