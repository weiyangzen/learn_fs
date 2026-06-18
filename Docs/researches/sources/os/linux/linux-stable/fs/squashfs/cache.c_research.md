# File Research: sources/os/linux/linux-stable/fs/squashfs/cache.c

## Summary
Provides the shared cache implementation for Squashfs metadata blocks, fragment blocks, and the intermediate data-block read cache used by `CONFIG_SQUASHFS_FILE_CACHE`.

## Key APIs
- `squashfs_cache_init()`, `squashfs_cache_delete()`.
- `squashfs_cache_get()`, `squashfs_cache_put()`.
- `squashfs_copy_data()`.
- `squashfs_read_metadata()`.
- `squashfs_get_fragment()`, `squashfs_get_datablock()`.
- `squashfs_read_table()`.

## Important Behavior
Each cache entry is a set of page-sized kmalloc buffers plus a page actor. `squashfs_cache_get()` searches round-robin, waits if all entries are in use, marks a newly selected entry pending, reads/decompresses it with `squashfs_read_data()`, and wakes waiters.

`squashfs_read_metadata()` reads arbitrary metadata byte ranges from packed metadata blocks, crossing block boundaries by following `entry->next_index`.

`squashfs_read_table()` reads an uncompressed on-disk table into a linear kmalloc buffer by building a page actor over the table buffer.

## Synchronization
The cache uses a spinlock for entry state, wait queues for whole-cache and per-entry contention, entry refcounts to prevent eviction, and a pending flag so concurrent users wait for a fill in progress.

## Risks
The cache assumes metadata and fragments fit into the configured block-size/page-array layout. Callers must release every entry with `squashfs_cache_put()`, including error entries, or cache capacity can be exhausted.
