# File Research: sources/os/linux/linux/fs/xfs/xfs_ioctl.h

## Role
Declares the native XFS ioctl and file attribute interfaces used by the VFS and compat ioctl layer.

## Main Declarations
- Forward declarations for `struct xfs_bstat`, `struct xfs_ibulk`, and `struct xfs_inogrp`.
- `xfs_ioc_swapext` for extent swap ioctl execution.
- `xfs_fileattr_get` / `xfs_fileattr_set` for VFS file attribute operations.
- `xfs_file_ioctl` and `xfs_file_compat_ioctl` for native and compat ioctl dispatch.
- `xfs_fsbulkstat_one_fmt` and `xfs_fsinumbers_fmt` formatter helpers for bulk inode query output.

## Interactions
Included by the main ioctl implementation, compat ioctl implementation, and inode operation setup. It provides the shared function surface that lets `xfs_ioctl32.c` delegate native-compatible commands and reuse native bulk output formatters for x32/native-layout cases.

## Invariants
The header has no logic, but it establishes that native and compat ioctl dispatch remain separate while sharing common formatter and swapext/fileattr helpers.
