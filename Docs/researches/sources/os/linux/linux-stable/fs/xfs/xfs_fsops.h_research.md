# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_fsops.h

## Purpose

Declares filesystem operation entry points for growfs, reserve management, forced shutdown, and AG metadata reservation.

## Main API

- `xfs_growfs_data`
- `xfs_growfs_log`
- `xfs_reserve_blocks`
- `xfs_fs_goingdown`
- `xfs_fs_reserve_ag_blocks`
- `xfs_fs_unreserve_ag_blocks`

## Research Notes

This header exposes administrative filesystem operations to ioctl and mount/superblock code.
