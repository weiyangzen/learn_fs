# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_handle.h

## Purpose

Declares XFS handle, by-handle xattr, attr list, and parent-pointer ioctl helper APIs.

## Main API

- By-handle attr operations:
  - `xfs_attrlist_by_handle`
  - `xfs_attrmulti_by_handle`
- Handle operations:
  - `xfs_find_handle`
  - `xfs_open_by_handle`
  - `xfs_readlink_by_handle`
  - `xfs_handle_to_dentry`
- Shared attr ioctl helpers:
  - `xfs_ioc_attrmulti_one`
  - `xfs_ioc_attr_list`
- Parent pointer operations:
  - `xfs_ioc_getparents`
  - `xfs_ioc_getparents_by_handle`

## Research Notes

This header is the ioctl-facing declaration point for handle-based administrative functions implemented in `xfs_handle.c`.
