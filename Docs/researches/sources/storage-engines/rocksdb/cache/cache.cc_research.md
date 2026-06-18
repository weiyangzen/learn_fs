# sources/storage-engines/rocksdb/cache/cache.cc

## Purpose
This file implements shared `Cache` and `SecondaryCache` factory/parsing behavior plus generic cache item helpers and default async-lookup behavior. It is part of RocksDB's cache abstraction layer rather than a concrete cache implementation.

## Important APIs, types, and functions
It defines `kNoopCacheItemHelper`, `kSliceCacheItemHelper`, and internal helper callbacks for slices. `lru_cache_options_type_info` maps string options to `LRUCacheOptions` fields such as capacity, shard bits, strict capacity, and priority-pool ratios. `comp_sec_cache_options_type_info` maps options for `CompressedSecondaryCacheOptions`.

`SecondaryCache::CreateFromString()` recognizes `compressed_secondary_cache://` URIs, parses the remaining option string through `OptionTypeInfo::ParseStruct`, and calls `NewCompressedSecondaryCache`; otherwise it delegates to `LoadSharedObject<SecondaryCache>`. `Cache::CreateFromString()` recognizes `null`, numeric capacity strings, `key=value` LRU option strings, and shared-object URIs. Async helpers implement synchronous fallback: `StartAsyncLookup()` calls `Lookup()`, `Wait()` calls `WaitAll()`, `WaitAll()` asserts that derived pending handles have been detached from pending caches, and `SetEvictionCallback()` stores a single callback with an assertion against overwriting non-empty callbacks.

## Control flow, state, and persistence
Factory methods create in-memory cache objects only. The slice helper has a no-op deleter that asserts if used, size/save callbacks for persisting slice bytes, and a create callback that is intentionally unsupported. Async lookup state lives in `AsyncLookupHandle`: base `Cache` implementations complete immediately by setting `result_handle`; derived caches can set `pending_handle`.

## Dependencies and integration points
The file integrates `rocksdb/cache.h`, `cache/lru_cache.h`, compressed secondary cache construction, customizable shared object loading, and options parsing infrastructure. It is used by option-string configuration paths, cache benchmarks, DB options parsing, and secondary-cache warming paths that need a `CacheItemHelper`.

## Risks and test signals
Factory parsing is string-sensitive; malformed LRU or secondary-cache option strings must return meaningful `Status` without partially swapping results. `kSliceCacheItemHelper` is safe only for borrowed slice-like objects because its deleter asserts. Async base behavior is intentionally synchronous, so derived implementations must preserve the pending-handle contract. Test via option parsing, URI loading, LRU creation, compressed secondary cache creation, async lookup tests, and secondary-cache save/create paths.
