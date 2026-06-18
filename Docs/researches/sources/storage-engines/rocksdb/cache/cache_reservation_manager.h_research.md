# sources/storage-engines/rocksdb/cache/cache_reservation_manager.h

## Purpose
This header declares the cache reservation abstraction, its dummy-entry implementation, and a mutex-protected concurrent wrapper. The abstraction lets RocksDB reserve block-cache capacity for memory consumed by related structures that are not themselves normal block cache entries.

## Important APIs, types, and functions
`CacheReservationManager` defines the interface: `UpdateCacheReservation(new_memory_used)`, delta-based `UpdateCacheReservation(memory_used_delta, increase)`, `MakeCacheReservation(incremental_memory_used, handle*)`, `GetTotalReservedCacheSize()`, and `GetTotalMemoryUsed()`. `CacheReservationManagerImpl<R>` implements the interface for a `CacheEntryRole`, with nested RAII `CacheReservationHandle`, a static dummy entry size of 256 KiB, deleted copy/move operations, delayed-decrease configuration, helper test access, and private increase/decrease/key-generation methods.

`ConcurrentCacheReservationManager` wraps any `CacheReservationManager` with a mutex. Its nested handle holds both the wrapper manager and an underlying handle; destruction locks the wrapper before resetting the underlying handle. The wrapper serializes absolute updates, delta updates, handle creation, and total memory reads. `GetTotalReservedCacheSize()` intentionally forwards without locking to the underlying implementation's atomic reserved-size read.

## Control flow, state, and persistence
The implementation reserves cache state indirectly by holding dummy entry handles. The concurrent wrapper owns a shared manager pointer and a mutex; the nested handles keep the wrapper alive until their underlying reservations are released. State is volatile and bounded by target cache lifetime.

## Dependencies and integration points
The header depends on cache entry roles, cache keys, typed cache placeholders, `Slice`, `Status`, and coding utilities. It is used by `charged_cache.cc` and other components that need to charge memory against a shared cache.

## Risks and test signals
The base implementation warns that callers must use either absolute updates or RAII handles, not both, to avoid unexpected accounting. The non-concurrent implementation's `memory_used_` and handle vector require external synchronization. `ConcurrentCacheReservationManager::MakeCacheReservation()` resets `*handle` even if the underlying call returns non-OK, so callers must handle status and returned handle carefully. Test with concurrent deltas, RAII handle destruction ordering, manager lifetime with outstanding handles, and role-specific helper identity.
