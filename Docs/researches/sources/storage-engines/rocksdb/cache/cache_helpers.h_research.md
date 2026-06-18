# sources/storage-engines/rocksdb/cache/cache_helpers.h

## Purpose
This header defines generic cache-handle utilities, including typed value extraction, pointer-to-slice keys, a movable RAII handle guard, aliasing shared-pointer construction, and the `WarmInCache()` declaration.

## Important APIs, types, and functions
`GetFromCacheHandle<T>()` returns `static_cast<T*>(cache->Value(handle))`. `GetSliceForKey<T>()` treats an object pointer as a fixed-size byte key. `CacheHandleGuard<T>` owns a `Cache::Handle*`, caches the typed value pointer, releases the handle on destruction, disallows copying, supports move construction/assignment, exposes cache/handle/value accessors, can `Reset()`, and can `TransferTo(Cleanable*)` by registering `ReleaseCacheHandleCleanup`. `MakeSharedCacheHandleGuard<T>()` creates a shared wrapper guard and returns an aliasing `shared_ptr<T>` pointing to the cached value while keeping the handle alive. `WarmInCache()` is declared for reconstructing cache entries from saved bytes.

## Control flow, state, and persistence
The guard's state is just `Cache*`, `Cache::Handle*`, and `T*`. Move operations transfer those fields and clear the source. `TransferTo()` transfers cleanup responsibility to another object and clears the guard without releasing immediately. The header does not persist data.

## Dependencies and integration points
It depends on `rocksdb/advanced_cache.h` and `rocksdb/rocksdb_namespace.h`. It integrates with typed cache users, `Cleanable` ownership chains, table/block cache code that wants RAII over handles, and secondary-cache warm-in code.

## Risks and test signals
Type safety is manual: a caller using the wrong `T` gets an invalid cast. `GetSliceForKey()` uses raw object bytes and is only appropriate for stable, trivially represented keys. `TransferTo(nullptr)` clears the guard without releasing, so callers must provide a valid cleanable when transferring a non-empty guard. Test by move/reset/destructor paths, cleanup transfer, and typed shared guards under sanitizer builds.
