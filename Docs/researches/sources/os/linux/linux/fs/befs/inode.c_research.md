# File Research: sources/os/linux/linux/fs/befs/inode.c

## Purpose
Validates raw BeFS inodes before VFS inode construction.

## Main Function
- `befs_check_inode()`: checks:
  - inode magic equals `BEFS_INODE_MAGIC1`
  - inode’s self-recorded block address matches the VFS block number
  - `BEFS_INODE_IN_USE` flag is set

## Return Values
Returns `BEFS_OK` for usable inodes and `BEFS_BAD_INODE` for failed validation.

## Research Notes
This file performs focused structural sanity checks. Detailed inode conversion and VFS setup are handled in `linuxvfs.c`.
