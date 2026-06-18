# File Research: sources/os/linux/linux-stable/fs/xfs/Makefile

## Purpose

This Makefile assembles the XFS kernel module/object from libxfs code, high-level filesystem code, transaction/log code, optional feature code, and online scrub/repair components.

## Main Structure

- Adds include paths for trace events and `libxfs`.
- Builds `xfs.o` when `CONFIG_XFS_FS` is enabled.
- Compiles `xfs_trace.o` first because trace macros can expand heavily.
- Builds libxfs first, including:
  - AG and allocation files in this group: `xfs_ag.o`, `xfs_ag_resv.o`, `xfs_alloc.o`, `xfs_alloc_btree.o`.
  - Core metadata modules for attrs, bmap, btrees, directories, inodes, rmap, refcount, superblock, symlink remote, transactions, and types.
- Adds realtime libxfs objects when `CONFIG_XFS_RT` is enabled.
- Adds high-level XFS modules for file I/O, attrs, buffers, discard, health, ioctl, iomap, inode cache, mount, stats, sysfs, xattrs, and more.
- Adds transaction and log recovery modules.
- Adds optional objects for quota, ACL, sysctl, compat ioctls, pNFS, DAX memory failure notifications, drain hooks, live hooks, memory buffers, and in-memory btrees.
- Adds online scrub and online repair object lists under `CONFIG_XFS_ONLINE_SCRUB` and `CONFIG_XFS_ONLINE_REPAIR`.

## Relationship to This Group

- Directly compiles:
  - `libxfs/xfs_ag.o`
  - `libxfs/xfs_ag_resv.o`
  - `libxfs/xfs_alloc.o`
  - `libxfs/xfs_alloc_btree.o`
- Pulls in high-level `xfs_xattr.o`, while generic VFS xattr support is outside this Makefile in `fs/xattr.c`.

## Research Notes

The file is a useful dependency map for XFS: allocator and AG code are in `libxfs`, which is shared with userspace tooling patterns, while runtime filesystem behavior is layered above it. Conditional sections explain why many allocator and AG structures include hooks for realtime, rmap/refcount, scrub, repair, and debug features.
