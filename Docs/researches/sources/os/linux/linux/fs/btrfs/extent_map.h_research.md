# File Research: sources/os/linux/linux/fs/btrfs/extent_map.h

Read completely: 195 lines.

This header defines the in-memory Btrfs extent-map data model and public extent-map tree operations. Extent maps describe file logical ranges and their backing disk extents, holes, inline data, compression, preallocation, logging, pinning, generation, and reference state.

Core definitions:
- `EXTENT_MAP_LAST_BYTE`, `EXTENT_MAP_HOLE`, and `EXTENT_MAP_INLINE` are sentinel disk bytenr values above normal physical bytenrs.
- `EXTENT_FLAG_PINNED` prevents eviction/merging before a new extent is safely persisted.
- Compression flags encode zlib, LZO, and ZSTD.
- `EXTENT_FLAG_PREALLOC` marks preallocated extents.
- `EXTENT_FLAG_LOGGING` marks maps currently involved in log-tree work.
- `EXTENT_FLAG_MERGED` records that adjacent maps were combined in memory.

`struct extent_map`:
- Holds rb-tree node, logical `start` and `len`, physical `disk_bytenr` and `disk_num_bytes`, decompressed `offset` and `ram_bytes`, generation, flags, refcount, and modified-list node.
- Comments document how fields map to Btrfs file extent item fields and where inline/hole behavior differs.
- The structure is intentionally compact because large files may cache many maps.

`struct extent_map_tree`:
- Contains the rb-tree root.
- Contains `modified_extents` for fast-fsync tracking.
- Uses an rwlock for tree/list protection.

Inline helpers:
- Set and read compression flags.
- Test whether an extent map is compressed.
- Test whether a map is currently linked into the rb-tree.
- Compute effective block start: compressed maps use `disk_bytenr`, non-compressed regular maps use `disk_bytenr + offset`, and holes/inline maps return their sentinel.
- Compute exclusive logical end with overflow protection.

Declared operations:
- Tree init, lookup/search, add, remove, drop range, replace range, split map, unpin, clear logging, allocate/free, cache init/exit, and shrinker work initialization/freeing.

Important interactions:
- Consumed by Btrfs inode, file, writeback, fiemap, ordered extent, and fsync paths.
- Compression enum comes from Btrfs filesystem definitions.
- Fast-fsync behavior depends on callers preserving list and generation semantics.

Risk and correctness notes:
- Sentinel disk bytenr values must never be confused with normal physical addresses.
- `btrfs_extent_map_block_start()` intentionally differs for compressed and non-compressed extents.
- Callers must hold the appropriate `extent_map_tree` lock when mutating tree/list membership.
