# File Research: sources/os/linux/linux/fs/jfs/jfs_discard.h

## Purpose
Declares the JFS discard/TRIM entry points.

## API
- Forward declares `struct fstrim_range`.
- Declares `jfs_issue_discard(struct inode *ip, u64 blkno, u64 nblocks)`.
- Declares `jfs_ioc_trim(struct inode *ip, struct fstrim_range *range)`.

## Dependencies
- Implemented by `jfs_discard.c`.
- Used by `ioctl.c` and `jfs_dmap.c`.
