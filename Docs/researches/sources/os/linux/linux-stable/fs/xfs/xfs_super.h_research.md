# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_super.h

Header for XFS superblock/VFS integration declarations and build-option strings.

Key elements:
- Provides conditional quota declarations/stubs and `XFS_QUOTA_STRING`.
- Provides conditional ACL flag setup and `XFS_ACL_STRING`.
- Defines feature strings for security attributes, realtime, online scrub, online repair, verbose warnings, fatal assert, and debug/no-debug.
- Builds `XFS_BUILD_OPTIONS`, used in module startup and module description.
- `XFS_WQFLAGS` adds `WQ_SYSFS` to workqueues in debug builds only.
- Declares `xfs_flush_inodes`, `xfs_set_inode_alloc`, `xfs_export_operations`, `xfs_quotactl_operations`, `xfs_reinit_percpu_counters`, global `xfs_discard_wq`, and `xfs_debugfs_mkdir`.
- Defines `XFS_M(sb)` to recover `struct xfs_mount *` from `sb->s_fs_info`.

Research notes:
- This header centralizes compile-time feature exposure for user-visible module descriptions.
- `XFS_WQFLAGS` changes workqueue observability under `DEBUG`, which is relevant when debugging mount workqueue behavior.
