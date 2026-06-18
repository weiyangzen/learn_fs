# File Research: sources/local-fs/btrfs-linux/fs/btrfs/xattr.h

This header exposes Btrfs xattr operations and the VFS handler table.

Declared API:
- `btrfs_xattr_handlers[]` is the null-terminated array of VFS xattr handlers for `security.*`, `trusted.*`, `user.*`, and `btrfs.*`.
- `btrfs_getxattr()` reads one full-name xattr.
- `btrfs_setxattr()` sets, replaces, creates, or removes one full-name xattr using an existing Btrfs transaction.
- `btrfs_setxattr_trans()` performs the same operation while starting or reusing a transaction.
- `btrfs_listxattr()` lists all xattr names for a dentry.
- `btrfs_xattr_security_init()` initializes LSM security xattrs for a new inode inside an existing transaction.

Cross-file relationships:
- Implemented by `xattr.c`.
- Used by inode creation paths, VFS xattr operations, ACL/security initialization, and property xattr handling.
- Depends only on forward declarations for `dentry`, `inode`, `qstr`, `xattr_handler`, and `btrfs_trans_handle`.

Important invariants:
- Callers of `btrfs_setxattr()` must already hold a transaction handle.
- Names passed to the lower-level get/set helpers are full xattr names, not suffix-only handler names.
- Security initialization expects the caller to supply a transaction handle via `fs_private`.
