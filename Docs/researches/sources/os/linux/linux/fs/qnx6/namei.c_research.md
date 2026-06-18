# File Research: sources/os/linux/linux/fs/qnx6/namei.c

## Role

Implements QNX6 dentry lookup.

## Key Function

- `qnx6_lookup()`:
  - rejects names longer than `QNX6_LONG_NAME_MAX`;
  - finds the inode number through `qnx6_find_ino()`;
  - loads the inode with `qnx6_iget()`;
  - returns `d_splice_alias()`.

## Research Notes

All directory scanning and long-name resolution lives in `dir.c`; this file is the VFS lookup wrapper.
