# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_filestream.h

## Purpose

Declares filestream lifecycle and AG selection APIs.

## Main API

- `xfs_filestream_mount`
- `xfs_filestream_unmount`
- `xfs_filestream_deassociate`
- `xfs_filestream_select_ag`
- `xfs_inode_is_filestream`

## Important Behavior

`xfs_inode_is_filestream` returns true when the mount has global filestreams enabled or the inode has the filestream inode flag.

## Research Notes

This header is the allocation-layer interface to filestream policy.
