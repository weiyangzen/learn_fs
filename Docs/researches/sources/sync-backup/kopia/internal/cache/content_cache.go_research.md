## sources/sync-backup/kopia/internal/cache/content_cache.go

Purpose: implements content caching for pack blob ranges, either by individual content IDs or by whole blobs.

Important APIs/types/functions: `ContentCache`, `Options`, `NewContentCache`, `ContentIDCacheKey`, `BlobIDCacheKey`, `contentCacheImpl`, `GetContent`, `PrefetchBlob`, and `CacheStorage`.

Control flow, state, and persistence: content IDs and blob IDs are key-mangled to spread sharded cache paths. In full-blob mode, `GetContent` locks by blob, checks cached full blob ranges, fetches and stores the full blob on miss, then slices output. In partial mode, it shared-locks the blob to avoid racing with prefetch, checks full blob cache, exclusive-locks the content ID, checks content cache, fetches the requested range, and stores it. Persistent state lives in `PersistentCache` over cache storage.

Dependencies and integration points: depends on underlying `blob.Storage`, persistent cache, HMAC protection, metrics, gather buffers, and `mutexMap` locking.

Risks and test signals: risks include incorrect range handling for `length=-1`, lock-key collisions with content/blob IDs, and stale cache after underlying blob mutation. Tests cover data/metadata modes, prefetch races, corruption recovery, cache failures, expiration, and passthrough.
