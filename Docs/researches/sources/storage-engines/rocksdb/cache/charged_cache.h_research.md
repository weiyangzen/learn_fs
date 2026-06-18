# sources/storage-engines/rocksdb/cache/charged_cache.h

## Purpose
This header declares `ChargedCache`, a cache wrapper that charges one cache's usage against another cache through reservations.

## Important APIs, types, and functions
`ChargedCache` derives from `CacheWrapper`. It declares overrides for `Insert`, `Lookup`, `WaitAll`, both `Release` signatures, `Erase`, `EraseUnRefEntries`, `SetCapacity`, `Name()`, and `GetCache()`. `kClassName()` returns `"ChargedCache"`. `TEST_GetCacheReservationManager()` exposes the internal `ConcurrentCacheReservationManager` for tests.

## Control flow, state, and persistence
The class holds a `std::shared_ptr<ConcurrentCacheReservationManager>`. All behavior is defined in the `.cc` file and is in-memory only.

## Dependencies and integration points
It depends on `rocksdb/advanced_cache.h` for `CacheWrapper` and `Cache` types plus RocksDB port headers. It forward declares `ConcurrentCacheReservationManager` to avoid exposing reservation implementation details to header users. It is intended for blob-cache/global-memory-limit integration.

## Risks and test signals
Because this is a wrapper, correctness depends on overriding every operation that can change target usage. New `Cache` mutation APIs added later could bypass reservation accounting unless `ChargedCache` is updated. Test by comparing target cache usage to block-cache reservation after each public operation and by exercising wrapper name/type checks.
