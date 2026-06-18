# File Research: sources/os/linux/linux-stable/fs/btrfs/xattr.h

## Purpose

`xattr.h` declares the Btrfs xattr API used by inode, security, and VFS integration code.

## Exports

- `btrfs_xattr_handlers`
  - VFS handler table for security, trusted, user, and Btrfs property xattrs.
- `btrfs_getxattr()`
  - Retrieve one xattr by full name.
- `btrfs_setxattr()`
  - Set/remove one xattr under an existing transaction.
- `btrfs_setxattr_trans()`
  - Set/remove one xattr while managing transaction start/end when needed.
- `btrfs_listxattr()`
  - List all xattr names on a dentry inode.
- `btrfs_xattr_security_init()`
  - Initialize security xattrs during inode creation.

## Dependencies

The header forward-declares `dentry`, `inode`, `qstr`, `xattr_handler`, and `btrfs_trans_handle`, and includes only `linux/types.h`.

## Research Notes

This is intentionally small and stable. It exposes only the xattr operations needed outside `xattr.c`, while hiding dir-item packing and handler implementation details.
