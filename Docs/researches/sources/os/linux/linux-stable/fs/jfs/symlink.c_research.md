# File Research: sources/os/linux/linux-stable/fs/jfs/symlink.c

## Purpose

Defines inode operation tables for JFS symbolic links.

## Operations

- `jfs_fast_symlink_inode_operations` uses `simple_get_link` for inline symlink targets stored in the inode.
- `jfs_symlink_inode_operations` uses `page_get_link` for symlink targets stored in file data pages.
- Both variants share `jfs_setattr` and `jfs_listxattr`.

## Notes

Creation and storage selection are implemented in `namei.c`; this file only exposes the VFS operation vectors consumed by that code.
