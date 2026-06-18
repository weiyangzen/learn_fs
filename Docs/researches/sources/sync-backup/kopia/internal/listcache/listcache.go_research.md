# sources/sync-backup/kopia/internal/listcache/listcache.go

Purpose: wraps a `blob.Storage` to cache `ListBlobs` results for selected prefixes in a separate cache storage, with HMAC verification and write/delete invalidation.

Important APIs/types/functions: `listCacheStorage`, `cachedList`, `saveListToCache`, `readBlobsFromCache`, `ListBlobs`, `PutBlob`, `DeleteBlob`, `FlushCaches`, `isCachedPrefix`, `invalidateAfterUpdate`, and `NewWrapper`.

Control flow: `ListBlobs` bypasses caching for unconfigured prefixes. For cached prefixes it reads and verifies cache data, falls back to listing the underlying storage, stores a JSON `cachedList` with expiry, and replays cached metadata to the callback. Writes and deletes delegate to underlying storage and then invalidate any cached prefix matching the blob ID. `FlushCaches` flushes the underlying storage and deletes cache blobs for all cached prefixes.

State/persistence behavior: cached list entries are persisted as HMAC-protected JSON blobs under their prefix IDs in `cacheStorage`. Expiry uses `cacheTimeFunc`, defaulting to `clock.Now`, and cached results can temporarily hide out-of-band storage changes until expiry or invalidation.

Dependencies/integration: depends on `repo/blob`, `internal/gather`, `internal/hmac`, `internal/clock`, JSON encoding, and repository logging. It is a consistency/performance layer around blob listing.

Risks/test signals: invalidation runs even if the underlying write/delete returns an error, which may drop caches conservatively. Cache storage failures are logged and ignored. HMAC protects integrity but not confidentiality.
