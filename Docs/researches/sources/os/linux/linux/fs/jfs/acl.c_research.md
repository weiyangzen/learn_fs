# File Research: sources/os/linux/linux/fs/jfs/acl.c

## Purpose
Implements POSIX ACL get/set/initialization support for JFS using JFS extended attributes and the transaction manager.

## Key Functions
- `jfs_get_acl()` maps ACL type to the POSIX ACL xattr name, reads the xattr via `__jfs_getxattr()`, converts it with `posix_acl_from_xattr()`, and returns `-ECHILD` for RCU lookup.
- `__jfs_set_acl()` converts an ACL to xattr bytes with `posix_acl_to_xattr()`, writes through `__jfs_setxattr()` under an existing transaction id, and updates the VFS cached ACL on success.
- `jfs_set_acl()` starts a transaction, locks `JFS_IP(inode)->commit_mutex`, updates inode mode for access ACLs with `posix_acl_update_mode()`, writes the ACL, marks mode/ctime dirty if needed, commits, and unlocks.
- `jfs_init_acl()` creates inherited ACLs for a new inode via `posix_acl_create()`, writes default and access ACLs when present, clears inode ACL caches otherwise, and synchronizes `mode2` low bits with `i_mode`.

## Error Handling
- Unsupported ACL types return `-EINVAL`.
- Missing ACL xattrs map `-ENODATA` to `NULL`.
- Allocation/conversion failures return standard kernel errors.
- Transaction commit result is returned from `jfs_set_acl()`.

## Dependencies
- Uses `jfs_xattr.h` for raw xattr helpers.
- Uses `jfs_txnmgr.h` for transaction begin/commit/end.
- Declared by `jfs_acl.h` and compiled only with `CONFIG_JFS_POSIX_ACL`.
