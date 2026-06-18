# sources/storage-engines/rocksdb/cache/secondary_cache_adapter.h

## Purpose
This header declares `CacheWithSecondaryAdapter`, a `CacheWrapper` that adds a secondary-cache tier to an existing primary cache. It exposes the public cache methods that need secondary behavior and the tiered-cache reservation/admission update hooks.

## Important APIs, Types, And Functions
The constructor accepts a target cache, a secondary cache, an admission policy, and a `distribute_cache_res` flag. Overridden cache methods include `Insert()`, `Lookup()`, `Release()`, `Value()`, `StartAsyncLookup()`, `WaitAll()`, `GetPrintableOptions()`, `Name()`, `SetCapacity()`, `GetSecondaryCacheCapacity()`, and `GetSecondaryCachePinnedUsage()`. Public update methods are `UpdateCacheReservationRatio()` and `UpdateAdmissionPolicy()`. Test accessors expose the wrapped primary and secondary caches. Private helpers declare eviction handling, secondary async lookup, promotion, dummy-result processing, object cleanup, and reservation state.

## Control Flow
The header establishes the adapter as the layer through which all primary cache operations pass when secondary caching is configured. Inserts and lookups are intercepted to manage secondary warming/promotion, while releases are intercepted to update placeholder reservation accounting when reservation distribution is enabled.

## State And Persistence Behavior
The declared state includes the secondary cache pointer, admission policy, reservation-distribution flag, primary reservation manager, secondary reservation ratio, a mutex dedicated to reservation accounting, and usage counters for placeholders and secondary-reserved bytes. All state is volatile; any durable behavior is delegated to the concrete `SecondaryCache`.

## Dependencies And Integration Points
The header depends on `cache/cache_reservation_manager.h` and `rocksdb/secondary_cache.h`. It is included by `lru_cache.cc`, compressed-secondary tests, and tiered-cache factory code. `CacheWithSecondaryAdapter` is used by `LRUCacheOptions::MakeSharedCache()` and `NewTieredCache()`.

## Risks And Edge Cases
The class stores an eviction callback into the target cache, so destruction order must be handled carefully. Reservation methods use a dedicated mutex to avoid deadlocks with cache operations. The dummy-object path means callers of `Value()` must never receive dummy handles; `ProcessDummyResult()` and `Promote()` enforce that in the implementation.

## Test Signals
Tests cover the public methods through `NewCache(..., secondary_cache)`, `NewTieredCache()`, async lookup APIs, capacity updates, and secondary capacity/pinned usage accessors. Test accessors are used in compressed-tiered tests to inspect underlying cache and secondary-cache usage.
