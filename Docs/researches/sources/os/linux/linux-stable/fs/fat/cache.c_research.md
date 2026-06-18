# File Research: sources/os/linux/linux-stable/fs/fat/cache.c

This file implements FAT inode cluster-chain caching and logical-to-physical block mapping.

Key responsibilities:
- Maintains a small per-inode LRU cache of contiguous cluster-chain runs, capped by `FAT_MAX_CACHE`.
- Initializes and destroys the slab cache for `struct fat_cache`.
- Invalidates cached cluster runs when cluster chains are changed.
- Walks FAT chains through `fat_ent_read()` when a requested file cluster is not cached.
- Converts file-relative sectors into physical block numbers for page cache, direct I/O, bmap, and directory access.

Important functions:
- `fat_cache_init()` / `fat_cache_destroy()` create and destroy the global `fat_cache` kmem cache.
- `fat_cache_lookup()` finds the best cached run at or before the requested file cluster and returns the mapped disk cluster.
- `fat_cache_add()` merges or inserts a new cluster run, replacing the LRU entry when the cache is full.
- `fat_cache_inval_inode()` removes all per-inode cache entries and advances `cache_valid_id` so stale in-flight cache additions are ignored.
- `fat_get_cluster()` resolves a file cluster index to a disk cluster by starting from `i_start`, using cache hits when possible, detecting loops and invalid/free entries, and adding contiguous runs back to the cache.
- `fat_get_mapped_cluster()` maps a sector to a physical block and reports how many contiguous sectors are available.
- `fat_bmap()` handles FAT12/16 fixed root-directory mapping and normal cluster-chain mapping, with EOF checks that differ for allocation and bmap callers.

State and locking:
- Per-inode cache state lives in `struct msdos_inode_info`: `cache_lru`, `nr_caches`, and `cache_valid_id`.
- Cache list operations are protected by `cache_lru_lock`.
- Cluster-chain reads depend on `fatent.c` FAT entry access.
- `mmu_private` is consulted only on allocation paths and assumes the caller holds the inode lock.

Failure behavior:
- Invalid start clusters, free entries inside chains, cluster-chain loops, and requests beyond EOF are reported through FAT error helpers and generally return `-EIO`.
- Allocation failure for a cache object only drops the optimization; it does not fail the block lookup.

Research relevance:
- This is the core FAT block-mapping helper below regular file I/O, directory reads, truncation, and allocation. Correct cache invalidation is critical because FAT cluster chains can be rewritten by truncate, free, and rename/unlink paths.
