# File Research: sources/os/linux/linux-stable/fs/ext2/symlink.c

## Purpose

Defines ext2 inode operations for normal and fast symbolic links.

## Main Responsibilities

- Provides `ext2_symlink_inode_operations` for page-backed symlinks.
- Provides `ext2_fast_symlink_inode_operations` for inline fast symlinks.
- Connects symlink inodes to common ext2 getattr, setattr, and xattr listing behavior.

## Key Operations

- Normal symlinks use `.get_link = page_get_link`.
- Fast symlinks use `.get_link = simple_get_link`.
- Both operation tables expose:
  - `.getattr = ext2_getattr`
  - `.setattr = ext2_setattr`
  - `.listxattr = ext2_listxattr`

## Dependencies

- Includes `ext2.h` for inode attribute helpers.
- Includes `xattr.h` for `ext2_listxattr`.

## Research Notes

The file is intentionally small because generic VFS/pagecache symlink helpers handle most symlink behavior. The ext2-specific part is operation table selection between page-backed and fast symlink storage.
