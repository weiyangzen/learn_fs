# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent_map.h

This header defines the extent-map data model and public cache API.

Primary definitions:
- Sentinel disk addresses distinguish special mappings: `EXTENT_MAP_HOLE`, `EXTENT_MAP_INLINE`, and `EXTENT_MAP_LAST_BYTE`.
- Extent-map flags track pinned not-yet-on-disk state, zlib/lzo/zstd compression, preallocation, logging, and synthetic merged maps.
- `struct extent_map` stores file offset, logical length, full on-disk extent bytenr and length, decompressed offset and size, generation, flags, reference count, rb-tree node, and modified-list node.
- `struct extent_map_tree` stores the rb-root, modified extents list, and protecting rwlock.

Important helpers:
- `btrfs_extent_map_set_compression()` and `btrfs_extent_map_compression()` encode/decode compression flags.
- `btrfs_extent_map_is_compressed()` provides a fast compressed check.
- `btrfs_extent_map_in_tree()` tests rb-tree membership.
- `btrfs_extent_map_block_start()` returns the physical start used for I/O, adding `offset` for uncompressed regular extents but not for compressed extents or sentinels.
- `btrfs_extent_map_end()` returns the exclusive logical end with overflow saturation.

API surface:
- Tree setup and lookup: `btrfs_extent_map_tree_init()`, `btrfs_lookup_extent_mapping()`, and `btrfs_search_extent_mapping()`.
- Lifecycle: slab init/exit, allocation, and reference release.
- Mutation: add, remove, drop range, replace range, split, unpin, and clear logging.
- Reclaim: `btrfs_free_extent_maps()` and `btrfs_init_extent_map_shrinker_work()`.

The header is the shared contract between file extent lookup, read/write submission, delalloc/ordered extent completion, fsync logging, fiemap, and memory reclaim.
