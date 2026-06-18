# File Research: sources/local-fs/kdave-linux/fs/btrfs/xattr.h

## Role

`xattr.h` is the public header for Btrfs extended attribute support.

## Exports

It declares:

- `btrfs_xattr_handlers`
- `btrfs_getxattr()`
- `btrfs_setxattr()`
- `btrfs_setxattr_trans()`
- `btrfs_listxattr()`
- `btrfs_xattr_security_init()`

## Dependencies

The header uses forward declarations for VFS and Btrfs transaction types, keeping consumers from needing the full implementation headers unless they use the function bodies.

## Relationship

The declarations correspond directly to the implementation in `xattr.c` and are used by inode, VFS, security initialization, and property-related paths.
