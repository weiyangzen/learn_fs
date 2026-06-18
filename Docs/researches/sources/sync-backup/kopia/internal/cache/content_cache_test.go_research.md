## sources/sync-backup/kopia/internal/cache/content_cache_test.go

Purpose: broader content cache tests for expiration, disk cache behavior, corruption recovery, and cache failure tolerance.

Important APIs/types/functions: `newUnderlyingStorageForContentCacheTesting`, `verifyCacheExpiration`, `TestDiskContentCache`, `verifyContentCache`, failure tests, `verifyStorageContentList`, and `withoutTouchBlob`.

Control flow, state, and persistence: tests populate cache entries, manipulate fake time, delete underlying blobs to infer eviction, create disk cache storage, read ranges, corrupt cached protected bytes and expect refetch, inject cache open/write/read failures, and assert reads still succeed from underlying storage when cache operations fail.

Dependencies and integration points: exercises content cache, persistent cache sweeping, protected cache encoding, map and faulty storages, and filesystem cache creation.

Risks and test signals: strong operational signal for resilience and eviction policy. It relies on fake time to avoid platform clock granularity issues. Some behavior depends on persistent cache internals not listed in this subset.
