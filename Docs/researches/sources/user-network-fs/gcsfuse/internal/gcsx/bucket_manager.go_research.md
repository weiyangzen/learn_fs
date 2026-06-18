<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager.go

Purpose: builds and manages configured GCS bucket wrappers for gcsfuse, including fake bucket support, dummy I/O, monitoring, debug logging, prefix restriction, rate limiting, stat cache, content-type handling, syncer setup, bucket type discovery, and temporary-object garbage collection.

Important APIs/types/functions: `BucketConfig`; `BucketManager` interface; `bucketManager`; `NewBucketManager`; `setUpRateLimiting`; `(*bucketManager).SetUpBucket`; `(*bucketManager).ShutDown`.

Control flow: `NewBucketManager` creates a shared stat LRU cache when configured and a cancellable GC context. `SetUpBucket` obtains a fake or storage-handle bucket, optionally wraps dummy I/O, monitoring, debug logging, prefix bucket, rate limiting, stat cache, content-type bucket, and `SyncerBucket`. It requires `TmpObjectPrefix`, forces bucket type discovery via `BucketType`, starts `garbageCollect` in a goroutine, and returns the syncer bucket.

State and persistence behavior: persistent state is remote GCS bucket/object data plus temporary objects under `TmpObjectPrefix`. In-memory state includes shared stat cache, storage handle, config, and GC cancellation. Garbage collection runs until `ShutDown`.

Dependencies and integration points: integrates `storage.StorageHandle`, `canned` fake bucket, dummy I/O bucket, monitoring bucket, debug bucket, prefix bucket, rate-limit wrappers, metadata stat cache, content type bucket, syncer/compose logic, metrics, logger, and bucket storage-layout metadata.

Risks: wrapper order changes semantics. Missing `TmpObjectPrefix` is fatal to setup. Stat cache shared across multibucket mounts must be namespaced by bucket. Rate limit capacity calculation can fail. GC goroutine lifecycle depends on `ShutDown` being called.

Test signals: companion tests cover construction, setup for single and multibucket mounts, and missing bucket errors. Other integration tests exercise stat cache, prefix, and syncer behavior indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager.go -->
