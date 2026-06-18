# File Research: sources/local-fs/btrfs-linux/fs/btrfs/acl.c

Implements POSIX ACL get/set operations through Btrfs extended attributes.

Key points:
- `btrfs_get_acl()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`.
- Rejects RCU ACL lookup with `-ECHILD`.
- Reads ACL xattr size first, allocates storage, then reads xattr content.
- Converts xattr bytes to `struct posix_acl` with `posix_acl_from_xattr(&init_user_ns, ...)`.
- `__btrfs_set_acl()` serializes ACLs with `posix_acl_to_xattr()`.
- Uses `memalloc_nofs_save()` while allocating serialized ACL xattrs under a transaction to avoid filesystem reclaim deadlocks.
- Default ACLs are only valid for directories; setting one on a non-directory returns `-EINVAL`, while clearing one is a no-op.
- Chooses `btrfs_setxattr()` when a transaction handle is supplied and `btrfs_setxattr_trans()` otherwise.
- Updates the VFS ACL cache with `set_cached_acl()` after successful storage.
- `btrfs_set_acl()` updates inode mode for access ACLs via `posix_acl_update_mode()` and rolls back mode on storage failure.

Role in system:
- Bridges Linux POSIX ACL infrastructure to Btrfs xattr persistence.
- Compiled only when `CONFIG_BTRFS_FS_POSIX_ACL` is enabled.
