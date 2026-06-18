# File Research: sources/os/linux/linux-stable/fs/btrfs/acl.c

## Summary
Implements Btrfs POSIX ACL get/set operations on top of Btrfs xattrs.

## Main Responsibilities
- Reads access and default ACL xattrs.
- Converts xattr bytes to `struct posix_acl`.
- Converts ACLs to xattr bytes for storage.
- Updates cached ACLs after successful writes.
- Adjusts inode mode when setting access ACLs.

## Important Behavior
`btrfs_get_acl()` does not support RCU lookup and returns `-ECHILD` when called in RCU mode. ACL values are fetched with a size probe followed by allocation and a second `btrfs_getxattr()`.

`__btrfs_set_acl()` supports either an existing transaction or creating its own xattr transaction. ACL-to-xattr conversion runs under `memalloc_nofs_save()` because callers may hold a Btrfs transaction. Default ACLs are valid only for directories.

## Risks
On access ACL set failure, `btrfs_set_acl()` restores the old inode mode. Allocation inside a transaction must remain NOFS to avoid filesystem reclaim deadlocks.
