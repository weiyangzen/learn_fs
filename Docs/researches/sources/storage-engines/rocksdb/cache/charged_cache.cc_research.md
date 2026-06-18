# sources/storage-engines/rocksdb/cache/charged_cache.cc

## Purpose
This file implements `ChargedCache`, a `CacheWrapper` that forwards operations to an underlying cache while reserving equivalent usage in a separate block cache through `ConcurrentCacheReservationManager`. It lets blob-cache or secondary cache memory count toward a global block-cache memory limit.

## Important APIs, types, and functions
The constructor stores the wrapped cache in `CacheWrapper` and creates a concurrent reservation manager backed by `CacheReservationManagerImpl<CacheEntryRole::kBlobCache>` against the provided block cache. `Insert()` forwards to `target_->Insert()` and, on success, updates reservation to `target_->GetUsage()` because insertion can evict entries. `Lookup()` forwards and updates reservation when helper/create callbacks are present, covering possible secondary-cache promotion into the primary cache. `WaitAll()` forwards async waits then updates usage for promotions that complete during waits. Both `Release()` overloads capture `target_->GetUsage(handle)` before forwarding release; if the entry was erased, they decrease reservation by that delta. `Erase()`, `EraseUnRefEntries()`, and `SetCapacity()` forward then refresh reservation to target usage.

## Control flow, state, and persistence
`ChargedCache` stores only the reservation manager in addition to `CacheWrapper` state. It has no disk persistence. Reservation state is dummy entries in the block cache, updated after mutating or promotion-capable operations.

## Dependencies and integration points
It depends on `cache/charged_cache.h` and `cache/cache_reservation_manager.h`. It integrates cache wrappers, blob cache memory accounting, block cache global budgets, secondary cache promotion, async lookup wait paths, and cache capacity changes.

## Risks and test signals
Reservation updates ignore errors via `PermitUncheckedError()`, so a full strict block cache can silently under-reserve. Release paths use per-handle usage deltas and assume the erased return value accurately signals whether reservation should decrease. Lookup updates only when `helper && helper->create_cb`, so promotion paths must supply a create-capable helper. Test with blob cache insert/lookup/release/erase, secondary cache promotion through `WaitAll`, block cache strict-capacity pressure, and capacity shrink evictions.
