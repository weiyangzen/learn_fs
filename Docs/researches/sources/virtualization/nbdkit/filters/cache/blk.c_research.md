# File Research: sources/virtualization/nbdkit/filters/cache/blk.c

Purpose: block-level backing store for the cache filter.

Key details:
- Creates an unlinked temporary file under `TMPDIR` or `LARGE_TMPDIR`.
- Chooses `blksize` as `max(cache-min-block-size, statvfs.f_bsize)` to support hole punching.
- Maintains a two-bit bitmap per block: not cached, clean, or dirty.
- Initializes and resizes bitmap/LRU state alongside the sparse temp file.
- `blk_read_multiple` groups adjacent cached or uncached runs; uncached reads go to the backend, cached reads go to the temp file.
- `cache-on-read` copies backend reads into the temp file as clean blocks.
- `blk_cache` explicitly caches a block or issues `posix_fadvise` for already cached blocks.
- `blk_writethrough` writes both temp cache and backend, marking clean.
- `blk_write` writes dirty blocks in writeback/unsafe mode, but delegates to writethrough for writethrough mode or writeback+FUA.
- `for_each_dirty_block` scans the bitmap and invokes a callback for dirty blocks.

Integration notes:
- Callers are required to hold the cache filter’s exclusive lock around these functions.
- Calls `reclaim` before operations that may allocate more cache space.
