# sources/storage-engines/rocksdb/cache/tiered_secondary_cache.cc

## Purpose
This file implements the lookup and promotion logic for `TieredSecondaryCache`, which stacks a compressed secondary cache in front of an NVM secondary cache. It lets lookups consult compressed memory first and then NVM, while optionally saving NVM-returned compressed data back into the compressed secondary tier.

## Important APIs, Types, And Functions
`TieredSecondaryCache::MaybeInsertAndCreate()` is the create callback used when an NVM lookup returns saved data; it may call `InsertSaved()` on the compressed secondary cache before delegating to the original helper's `create_cb`. `Lookup()` first queries the compressed secondary cache (`target()`), then wraps the original helper/context and queries `nvm_sec_cache_` using the tiered helper. `WaitAll()` waits outstanding NVM result handles and completes tiered result handles.

## Control Flow
Lookup starts in the compressed secondary tier. A compressed-tier hit returns immediately and marks `kept_in_sec_cache=true` so the primary adapter does not spill it back. On compressed miss, synchronous lookup uses a stack `CreateContext`; asynchronous lookup allocates a `ResultHandle` embedding that context, starts the NVM lookup, and returns the wrapper if the NVM lookup is pending or available. During create, `MaybeInsertAndCreate()` records either a compressed-secondary promotion or skip, then invokes the upper-layer helper to materialize the cache object.

## State And Persistence Behavior
The file manages no durable state directly. It passes through compressed data from NVM into the compressed secondary cache unless `advise_erase` is set or the data is uncompressed. It records stats ticks for promotions and skips. Async state is held in `ResultHandle` and its embedded `CreateContext` until `WaitAll()` completes it.

## Dependencies And Integration Points
The implementation depends on `cache/tiered_secondary_cache.h` and `monitoring/statistics_impl.h`. It is constructed by `NewTieredCache()` in `secondary_cache_adapter.cc` when an NVM secondary cache is configured with three-queue admission policy. It integrates the secondary-cache helper/create-callback contract with compressed-secondary `InsertSaved()`.

## Risks And Edge Cases
The implementation assumes NVM results represent `CacheTier::kVolatileTier` for now. Asynchronous lookup stores a pointer to the lookup key in the embedded context, so caller-managed key lifetime must remain valid for pending lookups. `kept_in_sec_cache` is forced true to avoid re-spill loops. `WaitAll()` must skip already-ready compressed-tier handles and only wait wrapped NVM handles.

## Test Signals
Compressed-secondary tiered tests exercise this through `NewTieredCache()` and admission policies. They validate promotion/skipping behavior indirectly via successful lookups, cache usage movement, and dynamic tiered-cache updates.
