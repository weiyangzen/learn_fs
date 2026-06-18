# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_acl.h

Small ACL interface header.

Behavior:
- With `CONFIG_JFS_POSIX_ACL`, declares `jfs_get_acl()`, `jfs_set_acl()`, and `jfs_init_acl()`.
- Without ACL support, provides an inline `jfs_init_acl()` stub returning success.

Integration:
- Lets inode/name creation code call ACL initialization unconditionally while making ACL support optional.
