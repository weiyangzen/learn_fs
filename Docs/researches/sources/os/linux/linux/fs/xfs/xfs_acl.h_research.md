# File Research: sources/os/linux/linux/fs/xfs/xfs_acl.h

Compile-time interface for XFS POSIX ACL support.

Key elements:
- Under `CONFIG_XFS_POSIX_ACL`, declares `xfs_get_acl`, `xfs_set_acl`, `__xfs_set_acl`, and `xfs_forget_acl`.
- Without ACL support, maps `xfs_get_acl` and `xfs_set_acl` to `NULL`, makes `__xfs_set_acl` a no-op success, and makes `xfs_forget_acl` a no-op.

Dependencies:
- Consumed by inode/xattr code that must compile with or without POSIX ACL support.

Research notes:
- The no-op `__xfs_set_acl` behavior allows internal callers to avoid compile-time conditionals.
