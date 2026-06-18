<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_cache.h -->
# sources/storage-engines/rocksdb/include/rocksdb/advanced_cache.h

## Purpose

`advanced_cache.h` declares RocksDB's expert cache customization API. It defines the abstract `Cache` contract used by block cache implementations, secondary cache promotion/demotion callbacks, reference-counted handles, asynchronous lookup hooks, cache wrappers, and memory allocator integration. It is intentionally unstable compared with simpler public cache factory APIs.

## Important APIs, Types, and Functions

- `Cache` derives from `Customizable` and exposes opaque `Handle`, `ObjectPtr`, and `CreateContext` types.
- `Cache::Priority` defines `HIGH`, `LOW`, and `BOTTOM` eviction priority classes.
- `CacheItemHelper` stores C-style callbacks: deleter, size, save-to, create-from-secondary, entry role, and a no-secondary-compatible helper.
- Core cache operations: `Insert`, `CreateStandalone`, `Lookup`, `BasicLookup`, `Ref`, `Release`, `Value`, `Erase`, `NewId`, capacity/strict-limit controls, usage/pinned/charge queries, helper query, `EraseUnRefEntries`.
- Introspection/walking APIs: `ApplyToAllEntries`, `ApplyToHandle`, occupancy/address-count queries, printable options, `ReportProblems`, `GetHashSeed`.
- Secondary-cache capacity/pinned queries default to `NotSupported`.
- Experimental async APIs: `AsyncLookupHandle`, `StartAsyncLookup`, `Wait`, `WaitAll`, release-with-usefulness, and eviction callback.
- `CacheWrapper` forwards operations to a wrapped `Cache` and is the preferred base for instrumentation/customization.
- `kNoopCacheItemHelper` is an extern helper for entries needing no cleanup.

## Control Flow

The header defines contracts rather than implementation flow. Insertions take ownership of objects only on OK status and may attempt secondary-cache insertion when helper callbacks support it. Lookups first query primary cache and may query secondary cache when helper/create context are supplied. Returned handles must be released exactly once unless ownership is transferred through documented APIs. Async lookup handles are populated by callers, passed to `StartAsyncLookup()`, waited on with `Wait()`/`WaitAll()` when pending, and then consumed through `Result()`.

`CacheWrapper` forwards almost every virtual call to `target_`, including async methods and problem reporting. `ApplyToHandle()` unwraps a wrapper cache pointer before forwarding to the target so callbacks see target-compatible handles.

## State and Persistence Behavior

Cache implementations own in-memory cache entries and optionally coordinate with secondary caches that can persist serialized objects across process or system restarts. The API makes key repeatability and global uniqueness a caller responsibility when secondary caches are shared. Refcounts and handles define object lifetime. `DisownData()` deliberately leaks data during process shutdown for faster teardown and makes later cache use invalid.

## Dependencies and Integration Points

The header depends on `rocksdb/cache.h`, compression types, memory allocator APIs, options/config customization, slices, status, and cache entry roles. It integrates with block/table cache code, compressed and tiered secondary caches, memory reservation helpers, table readers, blob cache users, and custom cache implementations.

## Risks and Edge Cases

This is a sharp API. Callback exceptions are explicitly forbidden because RocksDB is not exception-safe. `CacheItemHelper` instances must outlive the cache and cached entries. Objects compatible with secondary cache cannot be null because null has sentinel meaning. Handle lifetime rules are strict: release-after-release, value access after release, or destroying a pending async handle are undefined. Secondary-cache create callbacks must copy input data and clean up after failed creation. Wrapper authors must override new virtual methods when the base `Cache` API grows, as the comment warns.

## Test Signals

Signals include cache insert/lookup/release ownership behavior, strict capacity failures, standalone charge behavior, deleter invocation, secondary-cache save/promote paths, async pending/ready/wait flows, wrapper forwarding correctness, apply-to-all iteration under concurrency, eviction callback ownership transfer, pinned usage accounting, and problem reporting from concrete caches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_cache.h -->
