# File Research: sources/os/linux/linux/fs/jfs/jfs_acl.h

## Purpose
Declares JFS ACL functions and provides a no-op initializer when POSIX ACL support is disabled.

## API
- With `CONFIG_JFS_POSIX_ACL`: declares `jfs_get_acl()`, `jfs_set_acl()`, and `jfs_init_acl()`.
- Without `CONFIG_JFS_POSIX_ACL`: `jfs_init_acl()` inline returns 0 so inode creation code can call it unconditionally.

## Dependencies
- Expects transaction id type `tid_t`, `struct inode`, `struct dentry`, and `struct posix_acl` from included surrounding headers.
