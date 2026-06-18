# File Research: sources/teaching/minix/minix/lib/libminixfs/cache.c

This is the core `libminixfs` block buffer cache. It maintains an LRU list of buffers, a hash table keyed by block number, dirty-state tracking, optional VM secondary cache integration, read-ahead, scattered I/O, invalidation, and dynamic cache sizing.

Key state:
- `buf`: buffer array.
- `buf_hash`: hash table for `(dev, block)` lookup.
- `front`/`rear`: LRU free-buffer list.
- `bufs_in_use`: count of buffers currently checked out.
- `nr_bufs`: current buffer pool size.
- `fs_block_size`: active filesystem block size, default `PAGE_SIZE`.
- `vmcache` and `may_use_vmcache`: VM cache policy.
- `fs_btotal`/`fs_bused`: filesystem block usage for sizing heuristics.

Major exported functions:
- `lmfs_buf_pool`: initializes/resizes the buffer pool.
- `lmfs_set_blocksize`: changes block size and enables VM cache only for page-multiple block sizes.
- `lmfs_get_block`, `lmfs_get_block_ino`, `lmfs_get_partial_block`: acquire buffers.
- `lmfs_put_block`: release buffers.
- `lmfs_markdirty`, `lmfs_markclean`, `lmfs_isclean`: dirty-state helpers.
- `lmfs_free_block`: invalidate a freed block and ask VM to forget it.
- `lmfs_zero_block_ino`: creates a VM-cache-visible zero block for sparse-file holes using fake high device offsets.
- `lmfs_readahead`, `lmfs_prefetch`, `lmfs_readahead_limit`: prefetch helpers.
- `lmfs_flushdev`, `lmfs_flushall`: dirty writeback.
- `lmfs_invalidate`: purges all blocks for a device and clears VM cache.
- `lmfs_set_blockusage`, `lmfs_change_blockusage`: update usage counters and trigger heuristic resizing.
- `lmfs_fs_block_size`, `lmfs_may_use_vmcache`, `lmfs_setquiet`.

Cache acquisition flow:
- Lookup first checks local hash table.
- If present and not VM-evicted, the buffer is locked, refcounted, and returned.
- If VM marked it evicted, local state is invalidated.
- Otherwise the LRU front buffer is recycled.
- Dirty recycled buffers are flushed through `freeblock`.
- The requested block may be mapped from VM cache using `vm_map_cacheblock`.
- `PEEK` returns `ENOENT` if absent.
- `NORMAL` reads from the block driver; `NO_READ` allocates memory without disk read.

Writeback and read-ahead:
- `read_block` uses `bdev_read` or `bdev_gather` depending on block size.
- `rw_scattered` groups contiguous buffers into block-driver gather/scatter requests.
- `lmfs_readahead` obtains buffers with `NO_READ` then fills them in one or more gathered reads.
- `lmfs_prefetch` selects one contiguous range around the most important block.
- `lmfs_flushdev` collects cleanly releasable dirty buffers for a device and writes them sorted by block number.

VM cache integration:
- On release, buffers may be handed to VM with `vm_set_cacheblock`.
- VM-cache handoff includes inode and inode-offset metadata for mmap.
- Freed blocks are forgotten with `vm_forget_cacheblock`.
- Device invalidation calls `vm_clear_cache` even if VM caching is currently disabled.

Dynamic sizing:
- Cache size is based on VM free/cache memory and filesystem usage.
- Rechecks happen after block usage changes by about 10MB or during flush-all.
- Resizing requires no buffers in use.

Notable implementation risks:
- Several static arrays and static local pointers are used; this code assumes filesystem-server threading/context constraints.
- `get_block_ino` contains a comment about a race against `VMMC_EVICTED`.
- `lmfs_readahead_limit` can return `nr_bufs - 4` for larger caches but does not explicitly clamp to at least one after the `MIN(max_transfer, max_bufs)` expression.
