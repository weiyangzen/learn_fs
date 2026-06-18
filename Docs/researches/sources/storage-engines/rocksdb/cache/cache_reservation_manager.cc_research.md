# sources/storage-engines/rocksdb/cache/cache_reservation_manager.cc

## Purpose
This file implements `CacheReservationManagerImpl<R>`, which reserves capacity in a cache by inserting pinned dummy entries. It is used when memory consumed outside the block cache must still count toward a shared cache budget.

## Important APIs, types, and functions
`CacheReservationHandle` stores an incremental memory amount and a shared manager pointer; its destructor releases that amount. The manager constructor wraps the cache in `PlaceholderSharedCacheInterface<R>`, stores delayed-decrease mode, and initializes allocated and used counters. The destructor releases all remaining dummy handles with `ReleaseAndEraseIfLastRef()`.

`UpdateCacheReservation(new_mem_used)` records total memory used, then increases dummy entries until reserved size is at least the new usage, decreases them down to the smallest 256 KiB multiple still covering usage, or keeps them when unchanged. In delayed-decrease mode it keeps existing reservations until usage falls below 3/4 of the reserved size. `MakeCacheReservation()` updates total usage by an increment and returns an RAII handle. `IncreaseCacheReservation()` inserts dummy entries with unique cache-lifetime keys and `kSizeDummyEntry` charge. `DecreaseCacheReservation()` releases dummy handles from the vector tail. `GetNextCacheKey()` stores the generated `CacheKey` in a member so the returned `Slice` remains valid for the insert call. The file explicitly instantiates the template for table reader, compression dictionary, filter construction, misc, write buffer, file metadata, and blob cache roles.

## Control flow, state, and persistence
State is in-memory: the target cache wrapper, `delayed_decrease_`, atomic `cache_allocated_size_`, non-atomic `memory_used_`, dummy handle vector, and scratch `cache_key_`. There is no disk persistence. The class is explicitly not thread-safe except `GetTotalReservedCacheSize()`; concurrent callers should use `ConcurrentCacheReservationManager` from the header.

## Dependencies and integration points
It depends on cache roles, typed cache placeholders, `CacheKey`, `rocksdb/cache.h`, and block-based reader common definitions. It integrates with memory accounting for write buffers, blob caches, table readers, file metadata, and charged caches.

## Risks and test signals
Insert failures under strict capacity can leave partial dummy reservations while `memory_used_` records the requested amount, so callers must inspect returned `Status`. The 256 KiB quantum can over-reserve, and delayed decrease intentionally keeps stale reservations. `GetNextCacheKey()` returns a slice into mutable member storage and must only be used immediately. Test signals are reservation manager unit tests covering key generation, exact and rounded increases/decreases, strict-capacity failure recovery, delayed decrease thresholds, destructor cleanup, and RAII handle release.
