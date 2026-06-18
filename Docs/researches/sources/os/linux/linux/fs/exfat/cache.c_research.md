# File Research: sources/os/linux/linux/fs/exfat/cache.c

## Purpose
Provides a small per-inode LRU cache for translating file-relative cluster offsets to disk clusters, mainly accelerating FAT-chain traversal for fragmented files.

## Main Interfaces
- `exfat_cache_init`, `exfat_cache_shutdown`
- `exfat_cache_inval_inode`
- `exfat_get_cluster`

## Key Data Flow
The file defines `struct exfat_cache` ranges with file cluster, disk cluster, and contiguous count. `exfat_get_cluster()` starts from `ei->start_clu`, consults cached ranges with `exfat_cache_lookup()`, walks FAT entries as needed with `exfat_ent_get()`, detects contiguous disk extents, and adds/merges cache entries with `exfat_cache_add()`.

The cache is capped at `EXFAT_MAX_CACHE` entries per inode. When full, it reuses the least-recently-used entry. Cache invalidation frees all entries and bumps `ei->cache_valid_id` so stale in-flight cache descriptions are ignored.

## Dependencies
Depends on inode-private fields in `struct exfat_inode_info`, FAT entry reads from `fatent.c`, and spinlock-protected LRU lists.

## Notable Invariants And Risks
- `EXFAT_FREE_CLUSTER` as a file start is treated as filesystem corruption.
- No-FAT-chain files generally bypass deep FAT walking elsewhere; this cache mainly helps FAT-chain mode.
- Invalidation is intentionally coarse; callers must invalidate on truncation or chain mutation.
