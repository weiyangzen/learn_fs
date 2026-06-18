# File Research: sources/os/linux/linux/fs/ext4/extents_status.h

## Purpose

`extents_status.h` declares ext4's in-memory extent status tree types, status bit layout, helper accessors, and public APIs implemented by `extents_status.c`. It is the interface used by ext4 mapping, delayed allocation, fiemap, bigalloc, shrinker, and inode cleanup code to cache and query logical extent state.

## Status Encoding

- Extent status flags are stored in the high bits of `extent_status.es_pblk`.
- `ES_WRITTEN_B`, `ES_UNWRITTEN_B`, `ES_DELAYED_B`, `ES_HOLE_B`, and `ES_REFERENCED_B` define the bit positions.
- `ES_SHIFT` places status bits above the physical block number.
- `ES_MASK` masks the status-bit portion of `es_pblk`.
- `EXTENT_STATUS_WRITTEN`, `EXTENT_STATUS_UNWRITTEN`, `EXTENT_STATUS_DELAYED`, `EXTENT_STATUS_HOLE`, and `EXTENT_STATUS_REFERENCED` are the exported masks.
- `ES_TYPE_MASK` covers the mutually exclusive extent type bits.
- `ES_TYPE_VALID(type)` validates that exactly one extent type bit is present.

The referenced bit is not an extent type; it is an aging/reclaim hint used by the shrinker.

## Main Types

- `struct extent_status`
  - `rb_node`: node in the inode ES red-black tree.
  - `es_lblk`: first logical block.
  - `es_len`: length in filesystem blocks.
  - `es_pblk`: first physical block with status bits packed into high bits.
- `struct ext4_es_tree`
  - `root`: RB root of all cached status extents for an inode.
  - `cache_es`: recently accessed extent fast path.
- `struct ext4_es_stats`
  - Tracks shrink averages, cache hits/misses, scan timings, all-object counts, and shrinkable-object counts.
- `struct pending_reservation`
  - RB node plus logical cluster number for bigalloc pending cluster reservations.
- `struct ext4_pending_tree`
  - RB root for an inode's pending reservations.

## Inline Accessors

- `ext4_es_status()` returns all packed status bits.
- `ext4_es_type()` returns only the mutually exclusive type bits.
- `ext4_es_is_written()`, `ext4_es_is_unwritten()`, `ext4_es_is_delayed()`, and `ext4_es_is_hole()` test individual type states.
- `ext4_es_is_mapped()` is true for written or unwritten mappings.
- `ext4_es_set_referenced()`, `ext4_es_clear_referenced()`, and `ext4_es_is_referenced()` manage the reclaim aging bit.
- `ext4_es_pblock()` strips packed status bits and returns the stored physical block.
- `ext4_es_show_pblock()` displays placeholder `~ES_MASK` physical blocks as 0.
- `ext4_es_store_pblock()` updates the physical block while preserving status bits.
- `ext4_es_store_pblock_status()` stores physical block and status together and warns if the type encoding is invalid.

## Public APIs

Initialization and teardown:
- `ext4_init_es()`, `ext4_exit_es()`, `ext4_es_init_tree()`.
- `ext4_init_pending()`, `ext4_exit_pending()`, `ext4_init_pending_tree()`.
- `ext4_es_register_shrinker()`, `ext4_es_unregister_shrinker()`.

Extent status operations:
- `ext4_es_insert_extent()` for authoritative written/unwritten/hole state changes.
- `ext4_es_cache_extent()` for cache-only insertion of discovered on-disk extents or holes.
- `ext4_es_remove_extent()` for invalidating/removing cached status ranges.
- `ext4_es_find_extent_range()` for predicate-based range lookup.
- `ext4_es_lookup_extent()` for block mapping lookup with optional next extent and sequence output.
- `ext4_es_scan_range()` and `ext4_es_scan_clu()` for range/cluster predicate tests.
- `ext4_es_insert_delayed_extent()` for delayed allocation state and bigalloc pending reservation setup.
- `ext4_clear_inode_es()` for clearing discretionary cache entries.

Diagnostics and reporting:
- `ext4_seq_es_shrinker_info_show()` reports shrinker and cache stats through seq_file.

Pending reservation operations:
- `ext4_remove_pending()` removes a pending bigalloc cluster reservation.
- `ext4_is_pending()` tests whether a logical block's cluster has a pending reservation.

## Debug Configuration

- `ES_DEBUG__` enables verbose `es_debug()` logging; otherwise it compiles to `no_printk()`.
- `ES_AGGRESSIVE_TEST__` is defined in this header, enabling aggressive consistency-check code in `extents_status.c` when the corresponding conditional code is compiled.

## Integration Notes

- This header is consumed by ext4 extent mapping and allocation code to keep the ES cache coherent with on-disk extent tree updates.
- Packing status bits into `es_pblk` requires enough high bits to preserve physical block numbers; `extents_status.c` enforces this with `BUILD_BUG_ON(ES_SHIFT < 48)` during shrinker registration.
- Delayed and hole extents often use placeholder physical blocks such as `~0`; callers must use `ext4_es_pblock()` or `ext4_es_show_pblock()` rather than reading `es_pblk` directly.
- Only one type bit should be present at a time. Mixing type bits would break merge, lookup, and accounting assumptions.
