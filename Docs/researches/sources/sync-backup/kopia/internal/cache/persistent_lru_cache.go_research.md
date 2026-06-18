# sources/sync-backup/kopia/internal/cache/persistent_lru_cache.go

Purpose: implements Kopia's persistent on-disk LRU cache with optional cache-entry protection, write coalescing per key, metrics, and size-based sweeping.

Important APIs/types/functions: `PersistentCache`, `GetOrLoad`, `Put`, `CacheStorage`, `Close`, `SweepSettings`, `NewPersistentCache`, `contentMetadataHeap`, and internal helpers `getPartial`, `getPartialCacheHit`, `deleteInvalidBlob`, `sweepLocked`, and `initialScan`.

Control flow: `GetOrLoad` first attempts a full cache read, then takes a per-key exclusive lock, retries the read, invokes the caller fetcher on miss, records miss metrics, and writes protected data through `Put`. `Put` reserves `pendingWriteBytes`, sweeps while holding `listCacheMutex`, releases the lock for protection/storage I/O, writes via `PutBlob`, then updates heap metadata. `initialScan` lists all storage blobs into an age-ordered heap and immediately sweeps.

State and persistence behavior: durable state is in `Storage` blobs named by cache keys. In-memory state tracks LRU timestamps, total protected bytes, pending writes, and failed deletion reinsertion. Full reads verify HMAC/encryption protection; partial reads intentionally disable integrity verification. Touches update storage mtimes subject to `TouchThreshold`.

Dependencies/integration: integrates `cacheprot.StorageProtection`, `gather`, `blob.Storage` metadata, `clock.Now`, `metrics`, `timetrack`, `releasable`, and package-local mutex/metric helpers.

Risks/test signals: risks include stale heap accounting after storage write failure, partial reads bypassing integrity checks, and sweep behavior under delete errors. Tests cover LRU eviction, protection mismatch, corrupt data deletion, nil receiver behavior, storage faults, min sweep age, and default storage setup.
