# File Research: sources/os/linux/linux/fs/btrfs/ioctl.h

This header exposes the Btrfs ioctl/fileattr/io_uring entry points implemented in `ioctl.c`.

Exports:
- `btrfs_ioctl()` and `btrfs_compat_ioctl()` for VFS ioctl dispatch.
- `btrfs_fileattr_get()` and `btrfs_fileattr_set()` for VFS file attribute integration.
- `btrfs_ioctl_get_supported_features()` for feature-flag UAPI support.
- `btrfs_sync_inode_flags_to_i_flags()` to synchronize internal Btrfs inode flags into VFS inode flags.
- `btrfs_update_ioctl_balance_args()` to populate userspace balance status structs from live balance state.
- `btrfs_uring_cmd()` and `btrfs_uring_read_extent_endio()` for Btrfs io_uring encoded I/O commands and async read completion.

Design notes:
- The header uses forward declarations to avoid pulling large Btrfs and VFS structure definitions into callers.
- It is intentionally small and acts as the public boundary for ioctl-facing helpers used elsewhere in the filesystem.
