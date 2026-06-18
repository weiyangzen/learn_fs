# File Research: sources/local-fs/kdave-linux/fs/btrfs/acl.c

Purpose: Implements Btrfs POSIX ACL get/set operations using xattrs.

Main functions:
- `btrfs_get_acl(inode, type, rcu)`: rejects RCU lookup with `-ECHILD`, maps ACL type to xattr name, reads the xattr size, allocates a buffer when present, reads the value, and converts it with `posix_acl_from_xattr`.
- `__btrfs_set_acl(trans, inode, acl, type)`: validates type, rejects default ACLs on non-directories unless clearing, converts ACLs to xattr form under a NOFS allocation context, writes through either an existing transaction or `btrfs_setxattr_trans`, then updates the inode ACL cache.
- `btrfs_set_acl(idmap, dentry, acl, type)`: updates inode mode for access ACLs through `posix_acl_update_mode`, calls the internal setter, and restores the old mode on failure.

Dependencies: Uses VFS ACL types, POSIX ACL xattr conversion, Btrfs xattr APIs, transaction handles, and `AUTO_KFREE` cleanup from local misc helpers.

Error handling:
- Invalid ACL type returns `-EINVAL`.
- Missing ACL xattr returns `NULL`, not an error.
- Allocation failure returns `-ENOMEM`.
- Default ACL on a non-directory returns `-EINVAL` when setting and succeeds when clearing.
- Failed xattr write propagates the error and `btrfs_set_acl()` restores `i_mode`.

Risk notes: The NOFS context is important because ACL setting may occur while holding a transaction handle; reclaim-driven filesystem recursion could deadlock otherwise. Mode update and ACL xattr update are split, so rollback of `i_mode` on xattr failure is essential.
