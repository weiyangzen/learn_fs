# File Research: sources/os/linux/linux/fs/f2fs/extent_cache.c

## Summary
Implements F2FS in-memory extent caches. It maintains read extents for logical-to-physical block lookups and block-age extents for hot/warm/cold data-age decisions. Extents are stored per inode in cached red-black trees with global LRU-style lists and shrinker support.

## Main Responsibilities
- Validates on-disk inode read extent metadata.
- Creates, initializes, looks up, updates, merges, splits, shrinks, drops, and destroys extent trees.
- Supports two extent types: `EX_READ` and `EX_BLOCK_AGE`.
- Maintains largest read extent, cached extent-node hits, rb-tree hits, and global extent counters.
- Handles compressed read extents and device-aliasing constraints.
- Initializes/destroys extent cache slabs and per-superblock extent-cache state.

## Key APIs
- Validation/init: `sanity_check_extent_cache()`, `f2fs_init_read_extent_tree()`, `f2fs_init_age_extent_tree()`, `f2fs_init_extent_tree()`, `f2fs_init_extent_cache_info()`.
- Read cache: `f2fs_lookup_read_extent_cache()`, `f2fs_lookup_read_extent_cache_block()`, `f2fs_update_read_extent_cache()`, `f2fs_update_read_extent_cache_range()`.
- Age cache: `f2fs_lookup_age_extent_cache()`, `f2fs_update_age_extent_cache()`, `f2fs_update_age_extent_cache_range()`.
- Reclaim/lifetime: `f2fs_shrink_read_extent_tree()`, `f2fs_shrink_age_extent_tree()`, `f2fs_destroy_extent_node()`, `f2fs_drop_extent_tree()`, `f2fs_destroy_extent_tree()`.
- Slabs: `f2fs_create_extent_cache()`, `f2fs_destroy_extent_cache()`.

## Important Behavior
Read extent trees are enabled for regular files when the mount option permits them, plus special device-aliasing handling. Block-age trees are enabled for regular files and directories when age caching is enabled, but not for compressed or cold files.

Lookups first test the largest read extent, then the cached extent node, then the rb-tree. Hits update statistics and move extent nodes to the tail of the global extent list.

Updates invalidate overlapping ranges, split existing extents when large enough, merge compatible adjacent extents, insert new nodes, update the largest extent, and mark the inode dirty when the persisted largest extent changes. Small repeated splits can disable read extent caching by setting `FI_NO_EXTENT`.

Block-age updates compute age from `allocated_data_blocks` and previous age records using a weighted average. Invalid age updates can remove or skip age-cache entries.

Shrinking first frees zombie extent trees from evicted inodes, then removes LRU extent nodes from live trees using trylocks to avoid blocking heavily contended trees.

## State and Synchronization
Each extent tree has an rwlock for rb-tree and cached-largest state. Each extent type has a radix tree protected by `extent_tree_lock`, a global extent-node list protected by `extent_lock`, and zombie-tree accounting. Nodes and trees are allocated from dedicated slabs. Per-inode pointers in `F2FS_I(inode)->extent_tree[]` keep active trees reachable until inode eviction.

## Risks
Extent updates are sensitive to overlap, split, and merge boundaries. Read extents must never cache invalid physical addresses, compressed clusters incorrectly, or cross-device mappings that DIO cannot use. Device-aliasing inodes bypass normal read-cache lookup behavior and require strict extent validation. Shrinker and eviction paths must keep radix-tree entries, zombie lists, node lists, and counters synchronized.
