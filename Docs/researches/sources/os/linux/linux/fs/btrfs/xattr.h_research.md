# File Research: sources/os/linux/linux/fs/btrfs/xattr.h

## Purpose
Declares the Btrfs xattr API implemented by `xattr.c` and exports the VFS xattr handler table.

## Public API
- `btrfs_xattr_handlers[]`: handler table for `security.*`, `trusted.*`, `user.*`, and `btrfs.*`.
- `btrfs_getxattr()`: read a named xattr or query its size.
- `btrfs_setxattr()`: set/remove an xattr inside an existing Btrfs transaction.
- `btrfs_setxattr_trans()`: transaction-wrapping set/remove entry point.
- `btrfs_listxattr()`: list all xattr names for a dentry.
- `btrfs_xattr_security_init()`: initialize security xattrs for a newly created inode.

## Integration
The header forward-declares VFS and Btrfs transaction types, keeping include dependencies light for inode, file, and security initialization code.
