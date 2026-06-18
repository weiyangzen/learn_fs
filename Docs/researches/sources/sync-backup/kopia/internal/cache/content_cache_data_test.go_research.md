## sources/sync-backup/kopia/internal/cache/content_cache_data_test.go

Purpose: tests content-ID based data cache mode and passthrough fallback.

Important APIs/types/functions: `TestContentCacheForData` and `TestContentCacheForData_Passthrough`.

Control flow, state, and persistence: uses map-backed underlying storage and cache storage, fetches missing and present ranges, verifies cache key mangling and entry counts, closes the cache, tests a later miss, and validates prefetched full blob use after deleting underlying data.

Dependencies and integration points: validates `NewContentCache`, `ContentIDCacheKey`, `BlobIDCacheKey`, `PrefetchBlob`, and passthrough mode when no cache storage is configured.

Risks and test signals: confirms partial range caching and full-blob prefetch interplay. Does not test HMAC secret changes between cache instances.
