# File Research: sources/os/linux/linux/fs/xfs/xfs_super.h

## Purpose

`xfs_super.h` declares superblock-facing XFS interfaces and centralizes build option strings for module metadata and boot messages.

## Main Interfaces

- Feature string macros: `XFS_QUOTA_STRING`, `XFS_ACL_STRING`, `XFS_SECURITY_STRING`, `XFS_REALTIME_STRING`, `XFS_SCRUB_STRING`, `XFS_REPAIR_STRING`, `XFS_WARN_STRING`, `XFS_ASSERT_FATAL_STRING`, `XFS_DBG_STRING`, `XFS_VERSION_STRING`, and `XFS_BUILD_OPTIONS`.
- `XFS_WQFLAGS(wqflags)`: adds `WQ_SYSFS` to workqueue flags under `DEBUG`.
- Forward declarations for `struct xfs_inode`, `struct xfs_mount`, `struct xfs_buftarg`, and `struct block_device`.
- Function declarations: `xfs_flush_inodes`, `xfs_set_inode_alloc`, `xfs_reinit_percpu_counters`, and `xfs_debugfs_mkdir`.
- External operations: `xfs_export_operations` and `xfs_quotactl_operations`.
- Global workqueue declaration: `xfs_discard_wq`.
- `XFS_M(sb)`: converts a VFS superblock to `struct xfs_mount *`.

## Configuration Behavior

- Quota and ACL declarations compile to real functions/flags only when the corresponding config options are enabled; otherwise they compile to no-op helpers and empty strings.
- Realtime, scrub, repair, warning, fatal assert, and debug strings reflect build-time configuration.
- `set_posix_acl_flag` mutates `sb->s_flags` only when POSIX ACL support is enabled.

## Dependencies and Callers

- Consumed by `xfs_super.c` and other XFS files that need mount/superblock helpers.
- Build option strings are used for module description and init-time printk output.

## Research Notes

- This header is small but central for build-configuration reporting and VFS mount access.
- `XFS_BUILD_OPTIONS` must keep debug string last because it lacks a trailing comma fragment.
