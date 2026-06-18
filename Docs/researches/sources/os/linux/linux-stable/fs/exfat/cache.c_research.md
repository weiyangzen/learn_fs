# File Research: sources/os/linux/linux-stable/fs/exfat/cache.c

This file implements a small per-inode cluster mapping cache for FAT-chain lookup acceleration.

Key elements:
- Defines `struct exfat_cache`, holding a file-cluster start, disk-cluster start, and contiguous cluster count.
- Maintains up to `EXFAT_MAX_CACHE` entries per inode in `ei->cache_lru`, protected by `ei->cache_lru_lock`.
- `exfat_cache_init()` creates a slab cache for cache entries; `exfat_cache_shutdown()` destroys it.
- `exfat_cache_lookup()` finds a cache entry covering or preceding the requested file cluster range and returns the scan boundary before a later cache.
- `exfat_cache_add()` merges by file-cluster start, allocates a new cache entry when below the limit, or reuses the LRU tail when full.
- `exfat_cache_inval_inode()` drops all cached extents and bumps `cache_valid_id` so racing additions from stale traversals are ignored.
- `exfat_get_cluster()` maps a logical file cluster to a disk cluster, using the cache when possible and walking FAT entries with `exfat_ent_get()` when necessary.

Important dependencies:
- Used by `inode.c` through `exfat_map_cluster()`/`exfat_get_block()` for block mapping on fragmented files.
- Invalidated by `file.c` truncation and inode eviction when cluster chains change.
- For `ALLOC_NO_FAT_CHAIN` files, higher layers often bypass FAT walking; this cache mainly benefits `ALLOC_FAT_CHAIN`.

Failure/edge behavior:
- Detects invalid `start_clu == EXFAT_FREE_CLUSTER` as filesystem corruption.
- Handles EOF by returning `*count = 0`.
- Maintains `last_dclus` so append paths can link newly allocated FAT chains correctly.
- Cache entries store contiguous FAT extents, not arbitrary sparse mappings.
