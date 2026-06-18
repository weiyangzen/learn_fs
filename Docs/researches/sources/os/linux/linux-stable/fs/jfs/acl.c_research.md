# File Research: sources/os/linux/linux-stable/fs/jfs/acl.c

Implements POSIX ACL support on top of JFS extended attributes and transactions.

Key functions:
- `jfs_get_acl()` maps access/default ACL type to the corresponding xattr name, reads via `__jfs_getxattr()`, and decodes with `posix_acl_from_xattr()`.
- `__jfs_set_acl()` encodes ACLs with `posix_acl_to_xattr()` and stores/removes them via `__jfs_setxattr()`.
- `jfs_set_acl()` starts a transaction, locks `commit_mutex`, optionally updates inode mode through `posix_acl_update_mode()`, writes the ACL xattr, and commits.
- `jfs_init_acl()` derives default/access ACLs for newly created inodes and updates `mode2`.

Risk notes:
- RCU ACL lookup is unsupported and returns `-ECHILD`.
- ACL mode updates and xattr writes must remain in the same transaction to keep permissions consistent.
