# sources/storage-engines/rocksdb/cache/typed_cache.h

## Purpose
Provides type-safe C++ wrappers around RocksDB's low-level `Cache` API. The wrappers centralize typed handles, value deletion, secondary-cache serialization callbacks, guard construction, placeholder entries, and shared-cache ownership variants.

## Important APIs and Types
`BaseCacheInterface` stores either a raw or shared cache pointer and exposes release/cleanup helpers. `PlaceholderCacheInterface` reserves cache charge with null values and a role-only helper. `BasicTypedCacheHelperFns` upcasts/downcasts object pointers and deletes typed values, including array types. `BasicTypedCacheInterface<TValue>` implements typed `Insert`, `Lookup`, async lookup, `Guard`, `SharedGuard`, and `Value`. `FullTypedCacheHelperFns` adds `Size`, `SaveTo`, and `Create` callbacks for secondary-cache-compatible values. `FullTypedCacheInterface` adds `InsertFull`, `InsertSaved`, `LookupFull`, and `StartAsyncLookupFull`.

## Control Flow and State
The wrapper chooses basic versus full helpers based on `lowest_used_cache_tier`; volatile-only lookups avoid secondary-cache helper overhead. `InsertSaved` materializes a value through the full helper create callback before inserting it. The create path rejects non-volatile source tiers. State remains in the underlying `Cache`; this header contributes static `CacheItemHelper` singletons and typed ownership rules. Risks include reinterpret-casting typed handles, helper callbacks assuming `TValue::ContentSlice()`, and disabled custom-allocator object deletion. Integration points include blob value cache, secondary cache adapters, block cache users, and tests that use typed cache for in-memory fake caches.
