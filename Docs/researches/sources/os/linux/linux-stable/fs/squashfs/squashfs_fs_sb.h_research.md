# File Research: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs_sb.h

## Summary
Defines Squashfs in-memory superblock state, generic cache structures, and cache-entry state.

## Main Contents
- `struct squashfs_cache` and `struct squashfs_cache_entry`.
- `struct squashfs_sb_info`.

## Important Details
`squashfs_sb_info` owns decompressor selection, device block size, metadata/fragment/data caches, optional compressed-page cache mapping, id/fragment/xattr/inode lookup tables, the large-file meta-index cache, decompressor stream state, table starts, counts, error policy, decompressor thread ops, and max decompressor count.

Cache entries carry block identity, decompressed length, refcount, next metadata index, pending/error state, wait queue, data pages, and page actor.

## Risks
This is the central mount lifetime object. `super.c` cleanup paths must free every optional pointer consistently after partial mount failures and normal unmount.
