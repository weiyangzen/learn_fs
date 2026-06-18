# File Research: sources/os/linux/linux-stable/fs/ext4/extents_status.h

This header defines ext4's in-memory extent status API, status encoding, status-tree data structures, shrinker statistics, and pending cluster reservation interfaces.

Core definitions:
- Status bits: written, unwritten, delayed, hole, and referenced.
- `ES_SHIFT` and `ES_MASK`: reserve the high bits of `extent_status.es_pblk` for status flags while the low bits store the physical block.
- `ES_TYPE_MASK` and `ES_TYPE_VALID()`: enforce that the four extent type states are mutually exclusive.
- `struct extent_status`: RB-tree node plus logical start, length, and encoded physical block/status.
- `struct ext4_es_tree`: per-inode RB root plus one-entry recent lookup cache.
- `struct ext4_es_stats`: shrinker and cache hit/miss counters.
- `struct pending_reservation` and `struct ext4_pending_tree`: RB-tree representation of bigalloc pending cluster reservations.

Inline helpers:
- `ext4_es_status()`, `ext4_es_type()`, and type predicates classify ES entries.
- `ext4_es_is_mapped()` identifies written or unwritten mappings.
- referenced-bit helpers set/clear/query reclaim recency.
- `ext4_es_pblock()` masks out status bits to recover the physical block.
- `ext4_es_show_pblock()` formats the sentinel no-physical-block value as zero.
- `ext4_es_store_pblock()` preserves status while replacing the physical block.
- `ext4_es_store_pblock_status()` stores both physical block and a validated status type.

Public API groups:
- Extent status tree lifecycle and operations: init, insert, cache, remove, range find, lookup, scan range, scan cluster, clear inode cache.
- Shrinker lifecycle and reporting: register/unregister and seq-file info.
- Pending reservation lifecycle and operations: init, remove, query, delayed extent insertion, global init/exit.

Important constraints:
- Physical block numbers must fit below the high status bits.
- The referenced bit is not part of the mutually exclusive extent type.
- Pending reservations are only meaningful with bigalloc delayed-allocation accounting.
- The API separates authoritative modification (`ext4_es_insert_extent()`) from opportunistic caching (`ext4_es_cache_extent()`).
