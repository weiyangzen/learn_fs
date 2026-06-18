# File Research: sources/virtualization/qemu/block/qcow2-cache.c

## Purpose

Implements the shared in-memory cache used by qcow2 L2 table slices and refcount blocks. The cache provides fixed-size table slots, reference counting for checked-out entries, dirty tracking, LRU replacement, writeback ordering, and dependency handling between caches and protocol flushes.

## Main Data Structures

- `Qcow2CachedTable`:
  - `offset`: on-disk offset of the cached table, or zero for empty.
  - `lru_counter`: replacement/cleanup age marker.
  - `ref`: number of active users holding the cached table.
  - `dirty`: whether it must be written back.
- `Qcow2Cache`:
  - Array of `Qcow2CachedTable` entries.
  - Optional dependent cache pointer.
  - Entry count and table size.
  - `depends_on_flush` flag for write ordering after data/refcount writes.
  - Contiguous aligned `table_array` backing all cached table buffers.
  - LRU counters, including `cache_clean_lru_counter` for memory reclamation.

## Cache Allocation And Destruction

`qcow2_cache_create()` allocates metadata entries and one block-aligned memory array sized as `num_tables * table_size`. It asserts that table size is a power of two, at least the minimum qcow2 cluster size, and no larger than the image cluster size.

`qcow2_cache_destroy()` asserts that no entry is still referenced, then frees the table array and metadata.

## Address Helpers

- `qcow2_cache_get_table_addr()` maps a cache slot index to its table buffer.
- `qcow2_cache_get_table_idx()` maps a table pointer back to a cache slot and asserts correct alignment/range.
- `qcow2_cache_get_name()` identifies whether a cache is the refcount block cache, L2 table cache, or unknown for error messages.

## Memory Reclamation

`qcow2_cache_clean_unused()` scans for clean, unreferenced, nonempty entries whose LRU counter is older than the previous cleanup watermark:

- Clears their offsets and LRU counters.
- Releases contiguous ranges with `qcow2_cache_table_release()`.
- On Linux, `qcow2_cache_table_release()` uses `madvise(..., MADV_DONTNEED)` on page-aligned portions of table memory.

This drops resident memory without changing dirty state; only clean, unreferenced entries are eligible.

## Writeback And Flush Ordering

`qcow2_cache_entry_flush()` writes a single dirty cached table to disk:

- Ignores clean or empty entries.
- Flushes dependency cache first if `c->depends` is set.
- Otherwise flushes the protocol file if `depends_on_flush` is set.
- Performs overlap checks:
  - Refcount cache writes use `QCOW2_OL_REFCOUNT_BLOCK`.
  - L2 cache writes use `QCOW2_OL_ACTIVE_L2`.
- Emits block debug events.
- Writes the table with `bdrv_pwrite()`.
- Clears the dirty flag on success.

`qcow2_cache_write()` iterates all cache entries and flushes dirty entries. It preserves an `-ENOSPC` result priority if encountered.

`qcow2_cache_flush()` writes all dirty cache entries, then flushes the underlying protocol node.

## Dependencies

`qcow2_cache_set_dependency()` records that one cache must be flushed before another dirty cache is written. It first resolves existing dependencies that would conflict.

`qcow2_cache_depends_on_flush()` records that a cache must not be written until the protocol file has been flushed. This is used when metadata should only become visible after prior data/refcount writes are durable.

The dependency logic is important for qcow2’s metadata ordering: L2 table updates must not point to clusters before associated data and refcount state are safely written.

## Emptying The Cache

`qcow2_cache_empty()`:

- Flushes the cache.
- Asserts all entries are unreferenced.
- Clears every offset and LRU counter.
- Releases all table memory.
- Resets the cache LRU counter.

This is used when metadata will be modified outside the cache or when cached state must be invalidated.

## Lookup, Miss Handling, And Replacement

`qcow2_cache_do_get()` is the core lookup path:

- Rejects unaligned table offsets and signals image corruption.
- Uses a deterministic lookup start index based on offset.
- Scans the cache for a matching offset.
- Simultaneously tracks the unreferenced entry with the smallest LRU counter as replacement victim.
- If no unreferenced entry exists, aborts; current synchronous usage assumes this cannot happen.
- On miss:
  - Flushes the victim if dirty.
  - Clears its offset while loading.
  - Optionally reads table contents from disk.
  - Sets the new offset.
- Increments the entry refcount and returns the table pointer.

Public wrappers:

- `qcow2_cache_get()` loads table contents from disk.
- `qcow2_cache_get_empty()` allocates a cache slot without reading from disk, used for newly initialized metadata.

## Releasing And Dirtying Entries

`qcow2_cache_put()` decrements the entry refcount and sets a fresh LRU counter when the refcount reaches zero.

`qcow2_cache_entry_mark_dirty()` marks a referenced table dirty and asserts that the entry has a nonzero offset.

`qcow2_cache_is_table_offset()` returns the cached table pointer for a given offset if present.

`qcow2_cache_discard()` invalidates an unreferenced entry, clears offset/LRU/dirty state, and releases the memory for that slot.

## Error And Consistency Model

The cache enforces several key invariants:

- Cached table offsets must be nonzero and aligned to the table size.
- Dirty entries are never evicted without writeback.
- Referenced entries are not selected for replacement or discard.
- Cache users must `put` entries after use; destruction and emptying assert no outstanding references.
- Writeback includes qcow2 metadata overlap checks before writing.

## Interactions

This cache is used by qcow2 cluster/refcount code to manage:

- Active L2 table slices.
- Refcount blocks.
- Metadata update ordering between refcount blocks, data writes, and L2 pointer publication.

It relies on qcow2 state to identify cache type and block layer APIs for reads, writes, and flushes.
