# File Research: sources/os/linux/linux/fs/xfs/xfs_quotaops.c

## Role

Generic VFS `quotactl_ops` adapter for XFS. It maps Linux quota control operations and generic quota types/flags to XFS quota manager internals.

## Main Responsibilities

- `xfs_fs_get_quota_state` reports accounting/enforcement state, in-core dquot count, quota inode numbers, quota file blocks/extents, grace timers, and system-file flags.
- `xfs_fs_set_info` updates default quota timers through ID 0 `xfs_qm_scall_setqlim`.
- `xfs_quota_flags` maps `FS_QUOTA_*` flags to XFS `XFS_*QUOTA_*` flags.
- `xfs_quota_enable` and `xfs_quota_disable` wrap XFS enforcement transitions.
- `xfs_fs_rm_xquota` truncates quota files only when quotas are off.
- `xfs_fs_get_dqblk`, `xfs_fs_get_nextdqblk`, and `xfs_fs_set_dqblk` adapt generic `kqid` quota block calls to XFS dquot IDs and types.

## Important Behavior

The adapter performs read-only and quota-enabled checks before calling deeper quota manager functions. It uses `init_user_ns` for incoming quota IDs and converts returned scan IDs to the current user namespace.

## Exported Object

Defines `const struct quotactl_ops xfs_quotactl_operations`.

## Dependencies

Uses `xfs_qm.h`, `xfs_quota.h`, quota inode loading, dquot syscalls, and generic VFS quota structures.
