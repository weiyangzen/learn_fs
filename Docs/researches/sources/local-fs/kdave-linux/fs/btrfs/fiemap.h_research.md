# File Research: sources/local-fs/kdave-linux/fs/btrfs/fiemap.h

This header declares the Btrfs fiemap entry point.

Primary declaration:
- `btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo, u64 start, u64 len)` exposes the filesystem-specific fiemap implementation to inode/file operation code.

Dependencies:
- Includes `<linux/fiemap.h>` for `struct fiemap_extent_info` and fiemap flag definitions.
- Forward use of `struct inode` and `u64` comes from surrounding kernel headers included by consumers.

The header is intentionally minimal: all fiemap behavior, locking, cache buffering, btree walking, delalloc detection, and shared-extent checking live in `fiemap.c`.
