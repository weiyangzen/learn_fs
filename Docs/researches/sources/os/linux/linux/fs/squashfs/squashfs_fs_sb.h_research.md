# File Research: sources/os/linux/linux/fs/squashfs/squashfs_fs_sb.h

Defines in-memory SquashFS superblock and cache structures.

`struct squashfs_cache` and `struct squashfs_cache_entry` model the generic block cache, including spinlocks, wait queues, refcounts, pending/error state, buffers, and page actors.

`struct squashfs_sb_info` stores decompressor selection, device block geometry, metadata/fragment/data caches, compressed-page cache mapping, table indexes, meta-index cache, decompressor stream, table starts, format counts, error policy, threading ops, and thread limit.
