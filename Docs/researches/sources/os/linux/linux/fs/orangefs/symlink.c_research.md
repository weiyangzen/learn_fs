# File Research: sources/os/linux/linux/fs/orangefs/symlink.c

## Role

Defines OrangeFS symlink inode operations.

## Main Contents

`orangefs_symlink_inode_operations` wires symlink VFS methods to:

- `simple_get_link`
- `orangefs_setattr`
- `orangefs_getattr`
- `orangefs_listxattr`
- `orangefs_permission`
- `orangefs_update_time`

## Dependencies

Relies on symlink target caching and `inode->i_link` initialization performed during OrangeFS getattr/new inode handling.

## Research Notes

This file is intentionally minimal. Symlink behavior is mostly implemented in shared inode, permission, xattr, and getattr paths.
