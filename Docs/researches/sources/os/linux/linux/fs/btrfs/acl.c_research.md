# File Research: sources/os/linux/linux/fs/btrfs/acl.c

Purpose: Implements Btrfs POSIX ACL get/set operations using xattrs.

Main functions:
- `btrfs_get_acl()`: rejects RCU lookup with `-ECHILD`, maps ACL type to the access/default ACL xattr name, reads size, allocates a value buffer when present, reads the xattr, and converts it with `posix_acl_from_xattr()`.
- `__btrfs_set_acl()`: validates ACL type, rejects default ACLs on non-directories unless clearing, converts ACLs to xattr format in a NOFS allocation context, writes the xattr with or without an existing transaction, and updates the cached ACL.
- `btrfs_set_acl()`: updates inode mode for access ACLs through `posix_acl_update_mode()`, calls the internal setter, and restores the old mode on failure.

Error handling:
- Invalid ACL types return `-EINVAL`.
- Missing ACL xattrs return `NULL`, not an error.
- Allocation failure returns `-ENOMEM`.
- Default ACL on a non-directory returns `-EINVAL` when setting and succeeds when clearing.
- Xattr write errors propagate to the caller.

Risk notes: The NOFS allocation context avoids reclaim recursion while holding transaction state. The mode update and xattr update are not a single primitive, so restoring `i_mode` after failure is important.
