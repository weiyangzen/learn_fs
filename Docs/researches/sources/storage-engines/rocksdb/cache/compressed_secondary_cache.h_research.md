# sources/storage-engines/rocksdb/cache/compressed_secondary_cache.h

## Purpose
Declares RocksDB's compressed secondary cache implementation and its synchronous result handle. The class implements `rocksdb::SecondaryCache` with an internal cache that stores compressed or saved block data and supports the dummy-placeholder protocol described in the header comments.

## Important APIs, Types, And Functions
`CompressedSecondaryCacheResultHandle` implements `SecondaryCacheResultHandle` for synchronous lookups: `IsReady` is always true, `Wait` is a no-op, `Value` returns the materialized cache object, and `Size` returns its charge.

`CompressedSecondaryCache` overrides `SecondaryCache::{Insert,InsertSaved,Lookup,Erase,WaitAll,SetCapacity,GetCapacity,Deflate,Inflate,GetPrintableOptions}` and reports `Name()` as `"CompressedSecondaryCache"`. It exposes `SupportForceErase`, `TEST_GetUsage`, and private test access through `CompressedSecondaryCacheTestBase`.

Important private members include the internal `std::shared_ptr<Cache> cache_`, copied `CompressedSecondaryCacheOptions`, `Compressor`, `Decompressor`, `capacity_mutex_`, `ConcurrentCacheReservationManager`, and relaxed `disable_cache_`. `CacheValueChunk` and `malloc_bin_sizes_` support optional chunking to reduce allocator-bin waste.

## Control Flow
The declared API supports two data paths. `Insert` receives a live cache object plus helper callbacks, possibly inserts or observes a dummy, serializes the object, compresses when allowed, and stores tagged bytes in the internal cache. `InsertSaved` receives an already serialized payload and preserves the upstream compression type/source where supported. `Lookup` retrieves a real tagged payload, optionally decompresses it, calls the provided helper to recreate the object, optionally erases from secondary, and returns a synchronous result handle.

The header comments define the dummy control protocol. On lookup, if a dummy block with the key exists in primary, the secondary value is erased and promoted into primary; otherwise a primary dummy is inserted and a standalone handle is returned. On primary eviction, the secondary cache either replaces an existing dummy with real compressed data or inserts a secondary dummy of size zero.

## State And Persistence Behavior
State is volatile and scoped to the process. The internal cache stores either null dummy entries or allocated serialized byte/chunk payloads. `CacheValueChunk` owns linked chunk allocations and frees them through its helper. Capacity is mutable under `capacity_mutex_`, and capacity zero disables lookup/insert behavior through `disable_cache_`. The cache reservation manager lets external memory-pressure code deflate or inflate the cache's reservation.

## Dependencies And Integration Points
Depends on RocksDB cache reservation management, memory allocator support, advanced compression manager APIs, `rocksdb::SecondaryCache`, `rocksdb::Slice`, `rocksdb::Status`, and atomic utilities. The options object supplies LRU cache settings, compression type/options, allocator, excluded roles, capacity, and custom split/merge mode. The implementation is used through `NewCompressedSecondaryCache`/`CompressedSecondaryCacheOptions::MakeSharedSecondaryCache` and by primary-cache secondary adapters.

## Risks And Edge Cases
The class is synchronous despite using the secondary-cache result-handle abstraction; callers waiting for async behavior will observe immediate readiness. The dummy protocol means presence of a key can represent admission state rather than cached bytes. Split/merge mode owns chunks through raw linked allocations and is explicitly marked for cleanup in the implementation. `InsertSaved` support is narrower than the interface suggests: some source/type/mode combinations are accepted as OK but not stored as real data.

## Test Signals
Header-level behavior is validated through implementation tests in `cache/tiered_secondary_cache_test.cc`, blob secondary-cache tests, and stress-tool configurations. Useful observable signals are `SupportForceErase`, `TEST_GetUsage`, result-handle readiness/value/size, capacity get/set results, and the behavior of dummy hits versus real hits in statistics.
