# File Research: sources/os/linux/linux-stable/fs/btrfs/extent_map.h

## Purpose

`extent_map.h` defines the in-memory file extent map representation and declares the extent-map tree API used by Btrfs read, writeback, fiemap, fsync, and reclaim paths.

## Key Constants

- `EXTENT_MAP_LAST_BYTE` separates real disk bytenrs from sentinel values.
- `EXTENT_MAP_HOLE` marks logical holes.
- `EXTENT_MAP_INLINE` marks inline file extents.

## Extent Map Flags

- `EXTENT_FLAG_PINNED`: entry is not yet persisted and must not be evicted.
- `EXTENT_FLAG_COMPRESS_ZLIB`, `EXTENT_FLAG_COMPRESS_LZO`, `EXTENT_FLAG_COMPRESS_ZSTD`: compression type bits.
- `EXTENT_FLAG_PREALLOC`: preallocated extent.
- `EXTENT_FLAG_LOGGING`: extent is being logged.
- `EXTENT_FLAG_MERGED`: runtime-only indicator that adjacent maps were merged.

## `struct extent_map`

The structure is intentionally compact because many instances can exist. It stores:

- `rb_node` for the inode's extent rb-tree.
- Logical range: `start`, `len`.
- Physical/on-disk fields: `disk_bytenr`, `disk_num_bytes`, `offset`, `ram_bytes`.
- `generation` used for fsync and merged-map generation tracking.
- `flags`, `refs`, and `list` for modified extent tracking.

The comments explicitly distinguish regular, compressed, hole, and inline extent semantics.

## `struct extent_map_tree`

Contains the rb-tree root, modified extent list, and rwlock. Each Btrfs inode has one to cache file extent mappings.

## Inline Helpers

- `btrfs_extent_map_set_compression()` sets compression flag bits.
- `btrfs_extent_map_compression()` decodes compression type.
- `btrfs_extent_map_is_compressed()` checks compression efficiently.
- `btrfs_extent_map_in_tree()` checks rb-tree membership.
- `btrfs_extent_map_block_start()` returns physical start:
  - compressed extents use `disk_bytenr`;
  - regular extents use `disk_bytenr + offset`;
  - holes/inline return the sentinel.
- `btrfs_extent_map_end()` returns exclusive logical end and handles overflow.

## Exported API

The header exposes initialization, allocation/free, lookup/search, insertion, removal, range drop/replace, split, unpin, logging clear, and shrinker scheduling/init functions.

## Design Notes

The header documents that extent maps are cache objects, not exact persistent file extent records after merging. This distinction is essential for read I/O, fiemap, and fsync correctness.
