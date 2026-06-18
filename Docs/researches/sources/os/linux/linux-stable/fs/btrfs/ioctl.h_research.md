# File Research: sources/os/linux/linux-stable/fs/btrfs/ioctl.h

## Summary
Declares the Btrfs ioctl and encoded io_uring command interface used by the VFS-facing Btrfs code.

## Main Contents
- Forward declarations for VFS, io_uring, Btrfs inode, fs-info, and balance argument types.
- Entry points for regular and compat ioctl dispatch.
- File attribute get/set hooks.
- Helpers for supported features, inode flag synchronization, balance argument export, and io_uring encoded I/O completion.

## Key Interfaces
- `btrfs_ioctl()`.
- `btrfs_compat_ioctl()`.
- `btrfs_fileattr_get()`, `btrfs_fileattr_set()`.
- `btrfs_ioctl_get_supported_features()`.
- `btrfs_sync_inode_flags_to_i_flags()`.
- `btrfs_update_ioctl_balance_args()`.
- `btrfs_uring_cmd()`.
- `btrfs_uring_read_extent_endio()`.

## Risks
The header is small but exposes cross-subsystem boundaries: VFS ioctl dispatch, file attributes, balance state reporting, and io_uring encoded read completion. Implementations must keep UAPI and compat behavior stable.
