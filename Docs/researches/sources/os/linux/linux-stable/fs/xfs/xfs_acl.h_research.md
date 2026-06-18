# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_acl.h

## Purpose

Declares XFS POSIX ACL hooks and provides no-op stubs when ACL support is disabled.

## Key Contents

When `CONFIG_XFS_POSIX_ACL` is enabled:
- `xfs_get_acl`
- `xfs_set_acl`
- `__xfs_set_acl`
- `xfs_forget_acl`

When disabled:
- `xfs_get_acl` and `xfs_set_acl` are `NULL`
- internal set/forget helpers become no-ops.

## Research Notes

This header is the VFS ACL integration boundary for XFS.
