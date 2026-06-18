# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl.h

This header declares the native XFS ioctl-facing entry points and formatter helpers shared by ioctl and compat ioctl code.

Exports:
- `xfs_ioc_swapext` for extent swapping.
- `xfs_fileattr_get` and `xfs_fileattr_set` for VFS file attribute operations.
- `xfs_file_ioctl` for native ioctl dispatch.
- `xfs_file_compat_ioctl` for compat ioctl dispatch.
- `xfs_fsbulkstat_one_fmt` and `xfs_fsinumbers_fmt` for legacy bulkstat/inumbers formatting.

Role:
- Provides the interface between VFS file operations, native ioctl implementation, compat ioctl implementation, and bulk inode query formatting.
- Forward-declares `xfs_bstat`, `xfs_ibulk`, and `xfs_inogrp` to avoid pulling heavier headers into users.
