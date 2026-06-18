# File Research: sources/virtualization/nbdkit/filters/xz/blkcache.c

This file implements a small fixed-depth LRU cache for decompressed xz blocks. `new_blkcache` allocates the cache object and an array of block slots, initializing hit/miss stats. `free_blkcache` frees every cached block data pointer, the slot array, and the cache.

`get_block` linearly scans slots for a block containing the requested uncompressed offset. On a hit, it swaps the hit slot with slot 0 to mark it most recently used, updates hit stats, and returns the data plus start/size. On a miss it increments miss stats.

`put_block` evicts the least-recently-used slot at `maxdepth - 1`, shifts all slots down, and inserts the supplied data pointer at slot 0. Ownership of `data` transfers to the cache.

Risks and invariants: `put_block` assumes `maxdepth >= 1`, guaranteed by `xz.c` config validation. Cache access is not internally synchronized; the xz filter forces serialized requests. The LRU update swaps with slot 0 rather than doing a full move, which is simple but approximate.
