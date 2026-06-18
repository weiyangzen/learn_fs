# File Research: sources/local-fs/kdave-linux/fs/btrfs/ioctl.h

## Purpose

`ioctl.h` declares the Btrfs ioctl and file attribute interfaces implemented by `ioctl.c`. It is a narrow internal header for connecting VFS operation tables, compat ioctl support, feature reporting, balance-status formatting, inode flag synchronization, and io_uring encoded I/O support.

## Interfaces

Declared functions:

- `btrfs_ioctl()`
- `btrfs_compat_ioctl()`
- `btrfs_fileattr_get()`
- `btrfs_fileattr_set()`
- `btrfs_ioctl_get_supported_features()`
- `btrfs_sync_inode_flags_to_i_flags()`
- `btrfs_update_ioctl_balance_args()`
- `btrfs_uring_cmd()`
- `btrfs_uring_read_extent_endio()`

## Dependencies

The header forward-declares VFS and Btrfs types instead of including broader subsystem headers. It includes only `<linux/types.h>`, keeping compile dependencies low.

## Integration Notes

This header forms the contract between Btrfs file operations and the ioctl implementation. Any changes here affect mount/file operation wiring and io_uring command dispatch.
