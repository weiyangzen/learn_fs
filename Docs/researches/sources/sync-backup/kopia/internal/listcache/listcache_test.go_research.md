# sources/sync-backup/kopia/internal/listcache/listcache_test.go

Purpose: validates list caching, expiry, HMAC rejection, invalidation on wrapped writes/deletes, explicit flushing, and non-cached prefix passthrough.

Important APIs/types/functions: `NewWrapper`, `listCacheStorage`, `blobtesting.NewMapStorage`, `AssertListResultsIDs`, `faketime.NewTimeAdvance`, `PutBlob`, `DeleteBlob`, `FlushCaches`, and `ListBlobs`.

Control flow: the test builds real and cache map storages with independent fake clocks, wraps selected prefixes, and verifies the first list writes a cache blob. It mutates underlying storage directly to show cached invisibility, advances cache time to expire entries, writes/deletes through the wrapper to trigger invalidation, corrupts cache data to force HMAC rejection, flushes caches, and checks callback errors are propagated.

State/persistence behavior: uses in-memory map storages as stand-ins for persistent blob stores. Cached JSON/HMAC blobs are visible in the cache storage under prefix IDs.

Dependencies/integration: integrates listcache with blobtesting, faketime, gather bytes, and test logging. Package-internal access allows replacing `cacheTimeFunc`.

Risks/test signals: broad behavior coverage for cache consistency. It does not simulate cache storage put/delete failures beyond corrupted cache content.
