# File Research: sources/os/linux/linux-stable/fs/qnx6/namei.c

## Summary
Implements QNX6 dentry lookup.

## Main Responsibilities
- Reject names longer than `QNX6_LONG_NAME_MAX`.
- Search a directory with `qnx6_find_ino()`.
- Load the found inode with `qnx6_iget()`.
- Return the inode through `d_splice_alias()`.

## Key Interfaces
- `qnx6_lookup()` is the directory inode lookup operation.

## Cross-File Interactions
Uses directory search from `dir.c` and inode loading from `inode.c`.
