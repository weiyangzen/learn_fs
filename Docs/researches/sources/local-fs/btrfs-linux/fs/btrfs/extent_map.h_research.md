# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent_map.h

## Scope

This header defines the Btrfs extent-map data model, special disk address sentinels, extent-map flags, compression helpers, range helpers, and public extent-map tree APIs implemented in `extent_map.c`.

## Types And Constants

- `EXTENT_MAP_LAST_BYTE`, `EXTENT_MAP_HOLE`, and `EXTENT_MAP_INLINE` are special `disk_bytenr` sentinel values above valid physical addresses.
- Extent-map flags track pinned extents, compression algorithms, preallocation, logging, and maps merged from adjacent source maps.
- `struct extent_map` is a compact cached representation of file extents and holes. It intentionally may represent merged ranges, so fields match on-disk file extent items only before merging.
- `struct extent_map_tree` contains the rb-tree, modified-extents list, and rwlock for one inode.

## Inline Helpers

- `btrfs_extent_map_set_compression()` sets the compression flag matching a Btrfs compression type.
- `btrfs_extent_map_compression()` returns the compression type encoded in flags.
- `btrfs_extent_map_is_compressed()` tests compression flags efficiently.
- `btrfs_extent_map_in_tree()` tests rb-node membership.
- `btrfs_extent_map_block_start()` returns the physical start used for I/O, adding logical offset for uncompressed regular extents but not for compressed extents.
- `btrfs_extent_map_end()` returns exclusive logical end and saturates on overflow.

## Public API Surface

The header exposes tree initialization, lookup/search, add/remove/replace/drop/split operations, allocation/free, slab init/exit, unpinning, clearing logging state, memory-pressure reclamation, and shrinker work initialization.

## Dependencies And Consumers

It includes Btrfs `fs.h` for compression types and core structures and is consumed by inode read/write paths, fiemap, fsync/logging, ordered extent completion, page release, and direct/buffered I/O code that needs cached logical-to-physical mapping.

## Risks And Invariants

- `disk_bytenr` sentinels must be compared with `EXTENT_MAP_LAST_BYTE`; valid physical bytenrs are below that range.
- For compressed extents, `block_start()` intentionally ignores `offset`; callers must not apply uncompressed offset rules.
- Merged maps trade exact on-disk item boundaries for memory efficiency, so consumers needing exact file extent item boundaries must consult the tree.
- The structure is kept compact because many maps can exist under memory pressure.
