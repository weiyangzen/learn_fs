# File Research: sources/os/linux/linux-stable/fs/btrfs/acl.h

## Summary
Declares the Btrfs ACL interface and provides no-ACL stubs when POSIX ACL support is disabled.

## Main Responsibilities
- Exposes `btrfs_get_acl()`, `btrfs_set_acl()`, and `__btrfs_set_acl()` under `CONFIG_BTRFS_FS_POSIX_ACL`.
- Maps VFS ACL hooks to `NULL` when ACL support is disabled.
- Provides an `-EOPNOTSUPP` internal setter stub without ACL support.

## Risks
Callers that use `__btrfs_set_acl()` must handle `-EOPNOTSUPP` in non-ACL builds. Public VFS operation tables rely on `NULL` hooks to disable ACL behavior cleanly.
