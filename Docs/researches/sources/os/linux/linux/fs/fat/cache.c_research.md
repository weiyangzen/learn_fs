# File Research: sources/os/linux/linux/fs/fat/cache.c

## Purpose
Implements FAT per-inode cluster-chain lookup caching and block mapping. It speeds translation from file-relative cluster/block positions to on-disk clusters/sectors while handling FAT chain corruption, EOF, truncation races, and FAT12/16 fixed root directory mapping.

## Main Responsibilities
- Maintains a small per-inode LRU cache of contiguous cluster-chain runs, capped by `FAT_MAX_CACHE`.
- Resolves a file cluster index to an on-disk cluster via `fat_get_cluster()`.
- Maps logical sectors to physical sectors for buffered I/O and `bmap()`.
- Invalidates cached cluster mappings when the FAT chain changes.

## Key Interfaces
- `fat_cache_init()` / `fat_cache_destroy()`: create and destroy the slab cache for `struct fat_cache`.
- `fat_cache_inval_inode()`: drops all cached cluster-chain records for one inode and bumps `cache_valid_id`.
- `fat_get_cluster()`: walks the FAT chain from `MSDOS_I(inode)->i_start` or from a cache hit to find a requested cluster.
- `fat_get_mapped_cluster()`: converts a sector into FAT cluster plus intra-cluster offset and returns a physical block span.
- `fat_bmap()`: public mapping helper used by FAT address-space and directory code.

## Important Behavior
`fat_get_cluster()` treats `cluster == 0` as the inode start cluster and returns `FAT_ENT_EOF` if the requested cluster is past EOF. It detects invalid start clusters, free entries in chains, and probable loops using `s_maxbytes >> cluster_bits` as a traversal limit.

The cache records file cluster, disk cluster, and contiguous length. `fat_cache_lookup()` can return either an exact containing run or the nearest prior run, allowing traversal to resume partway through a chain. `fat_cache_add()` rejects stale lookups by comparing `fat_cache_id.id` against the inode `cache_valid_id`.

`fat_bmap()` has a special branch for the fixed FAT12/FAT16 root directory, whose data is not cluster-chain-backed. For normal files it checks EOF differently for live I/O versus `bmap()` callers.

## Dependencies
Uses `struct msdos_inode_info` cache fields from `fat.h`, FAT entry readers from `fatent.c`, and error reporting from `misc.c`.

## Research Notes
The cache is correctness-sensitive around chain mutation. The code deliberately invalidates cache entries on truncation/free paths rather than trying to update existing LRU entries. The dummy cache id path in `fat_get_cluster()` avoids adding a bogus cache when no useful prior mapping was found.
