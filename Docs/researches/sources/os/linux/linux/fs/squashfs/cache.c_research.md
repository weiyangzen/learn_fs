# File Research: sources/os/linux/linux/fs/squashfs/cache.c

Provides the generic SquashFS cache used for metadata blocks, fragment blocks, and optionally file data blocks in file-cache mode.

The cache is a fixed-size round-robin set of entries, protected by a spinlock plus wait queues. Entries have refcounts, pending state, per-entry waiters, error storage, and page-actor-backed PAGE_SIZE buffers.

`squashfs_cache_get()` handles lookup, eviction, blocking while all entries are busy, and filling missed entries via `squashfs_read_data()`. `squashfs_read_metadata()` walks packed metadata across compressed blocks using the metadata cache.

Also exposes helpers for fragment/data block lookup and `squashfs_read_table()`, which reads table ranges into kmalloc memory through a page actor.
