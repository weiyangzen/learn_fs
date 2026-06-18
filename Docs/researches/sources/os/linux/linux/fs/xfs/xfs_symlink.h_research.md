# File Research: sources/os/linux/linux/fs/xfs/xfs_symlink.h

## Purpose

`xfs_symlink.h` declares the kernel-only XFS symlink operations implemented in `xfs_symlink.c`.

## Main Interfaces

- `xfs_symlink`: create a symlink under a parent XFS directory.
- `xfs_readlink`: read an XFS symlink target.
- `xfs_inactive_symlink`: clean up symlink storage during inode inactivation.

## Dependencies and Callers

- Depends on declarations of `struct mnt_idmap`, `struct xfs_inode`, and `struct xfs_name` from included XFS/VFS headers in callers.
- Included by symlink implementation and XFS inode operation code.

## Research Notes

- This header intentionally contains only prototypes and include guards; behavior is entirely in `xfs_symlink.c`.
