# sources/storage-engines/rocksdb/cache/compressed_secondary_cache.cc

## Purpose
Implements `CompressedSecondaryCache`, a concrete `SecondaryCache` backed by an internal LRU cache that stores serialized block payloads, optionally compressed, with a small tag identifying source tier and compression type. It supports RocksDB's secondary-cache adapter by acting as a compressed off-primary block cache and using dummy placeholder entries to coordinate promotion/admission decisions between primary and secondary cache.

## Important APIs, Types, And Functions
Primary entry points are `CompressedSecondaryCache::Lookup`, `Insert`, `InsertSaved`, `Erase`, `SetCapacity`, `GetCapacity`, `Deflate`, `Inflate`, and `GetPrintableOptions`. Internal helpers are `MaybeInsertDummy`, `InsertInternal`, `SplitValueIntoChunks`, `MergeChunksIntoValue`, `GetHelper`, and `TEST_GetCharge`. The anonymous helpers define the stored value format and compute `GetHeaderSize`.

The on-cache value is either a length-prefixed tagged byte sequence or, when custom split/merge is enabled, a linked list of `CacheValueChunk` objects. The first two bytes of the tagged data encode `CacheTier source` and `CompressionType type`; payload bytes are the saved block representation or compressed saved data.

## Control Flow
Construction creates an internal LRU cache from `CompressedSecondaryCacheOptions`, builds a cache reservation manager, sets `disable_cache_` when capacity is zero, and acquires compressor/decompressor objects from the builtin V2 compression manager.

`Lookup` returns null immediately when disabled or when the internal LRU has no entry. If the found value is null, it is a dummy hit: the function releases it, records `COMPRESSED_SECONDARY_CACHE_DUMMY_HITS`, and returns null. For a real value, lookup reconstructs tagged bytes from chunks or a length-prefixed allocation, reads source and compression type, and if this cache compressed the value (`kVolatileCompressedTier`) it decompresses to an uncompressed saved slice and rewrites the source to `kVolatileTier`. It then calls the caller's `create_cb` to materialize a cache object. If `advise_erase` is true, it erases the real secondary value on release and immediately inserts a zero-charge dummy; otherwise it leaves the secondary value in place and sets `kept_in_sec_cache`.

`Insert` rejects null values. Unless forced, it calls `MaybeInsertDummy`; when no secondary entry exists yet, that function inserts a null dummy and `Insert` returns without storing real data. If a dummy or real entry already exists, `InsertInternal` serializes the object through `helper->saveto_cb`, optionally compresses if the source object is uncompressed and the role is not excluded, writes the two-byte tag, and inserts into the internal LRU either as chunks or as a length-prefixed allocation.

`InsertSaved` handles values already saved by an upstream tier. It rejects `kVolatileCompressedTier`, no-compression saved slices, and custom split/merge mode, then applies the same dummy admission check before storing through `InsertInternal` using the slice helper. Capacity changes are mutex-protected, update options and the internal cache capacity, and flip `disable_cache_`.

## State And Persistence Behavior
All data is volatile memory in the internal LRU cache. There is no disk persistence. Entries can be real tagged byte payloads or null dummy placeholders. Dummies are used as a state protocol: first primary-cache eviction inserts a zero-charge dummy in secondary; a later eviction with the same key can replace it with real data, while lookup with `advise_erase` can remove real data and restore a dummy.

Usage and charge are tracked by the internal cache. Non-split values charge either `malloc_usable_size` when available or tagged payload size. Split values charge the allocated chunk sizes, not just payload bytes, to reflect malloc bins. `Deflate` and `Inflate` update a `ConcurrentCacheReservationManager`, enabling integration with memory reservation systems. `disable_cache_` is a relaxed atomic boolean derived from capacity zero.

## Dependencies And Integration Points
Depends on `cache/cache_reservation_manager.h`, `memory/memory_allocator_impl.h`, `rocksdb/advanced_compression.h`, `rocksdb/secondary_cache.h`, `util/coding.h`, `util/compression.h`, `util/string_util.h`, perf context counters, LRU cache options inherited by `CompressedSecondaryCacheOptions`, and `Cache::CacheItemHelper` callbacks.

It integrates with `CacheWithSecondaryAdapter`, block cache item helpers, tiered secondary-cache tests, blob secondary-cache paths, DB stress options, and statistics/perf counters such as compressed bytes, uncompressed bytes, real insert count, dummy insert count, cache hits, and dummy hits.

## Risks And Edge Cases
`Lookup` assumes in-memory compressed data should decompress successfully and asserts before returning null on failure. Malformed tag bytes or mismatched helper behavior can produce wrong source/type creation calls. `InsertInternal` preallocates for original bytes before possible compression, so large values can temporarily require multiple copies; the code explicitly clears `merged_value` after decompression to reduce peak copies.

The dummy protocol is subtle: an initial non-forced insert often stores only a placeholder rather than data, which is intentional for admission but can look like a missed insert. `InsertSaved` silently returns OK for unsupported combinations, including no-compression saved data and custom split/merge, so callers must understand that OK does not always mean a real entry was stored. Custom split/merge currently uses raw `new char[]`, ignores the configured allocator, and has FIXME notes about fragmentation and overhead.

## Test Signals
Direct coverage is concentrated in `cache/tiered_secondary_cache_test.cc`, which exercises compressed secondary cache admission, lookup, dummy behavior, usage/charge, advise-erase, forced insertion, and split/merge-like capacity outcomes. Blob-cache integration is covered by `db/blob/blob_source_test.cc`, `db/blob/db_blob_basic_test.cc`, and direct-write blob tests. DB stress uses compressed secondary cache flags and can combine it with HyperClock or LRU primary caches. Runtime signals include `TEST_GetUsage`, `TEST_GetCharge`, statistics ticks, and perf counters.
