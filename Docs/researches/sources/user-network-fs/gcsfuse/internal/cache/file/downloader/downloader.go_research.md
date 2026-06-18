<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader.go

## Purpose
This file defines `JobManager`, the singleton mount-level coordinator for asynchronous object download jobs. Its role is deduplicating one `Job` per bucket/object path, configuring those jobs with cache paths, permissions, LRU file-info cache, concurrency limits, metrics, tracing, and file-cache settings, and removing jobs when they complete, fail, or are invalidated.

## Important APIs and types
`NewJobManager` constructs the manager and chooses a global weighted semaphore size from `FileCacheConfig.MaxParallelDownloads`, defaulting to effectively unlimited. `CreateJobIfNotExists` returns an existing job or creates a `Job` with a cache `FileSpec` derived from `util.GetDownloadPath`. `GetJob` returns a job by object and bucket name. `InvalidateAndRemoveJob` invalidates a job if present. `DownloadChunkSizeMb` exposes configured chunk size for sparse setup. `Destroy` invalidates all tracked jobs.

## Control flow and state behavior
The manager maintains a `map[string]*Job` keyed by `util.GetObjectPath(bucket, object)`. All map access is guarded by a `locker.Locker`. Job creation registers a callback that calls back into `removeJob`, letting the job remove itself from the manager after terminal cleanup. `InvalidateAndRemoveJob` intentionally releases the manager lock before calling `Job.Invalidate`; this avoids deadlock because invalidation eventually invokes the remove callback, which needs the same manager lock.

## Dependencies and integration points
The manager is configured by `cfg.FileCacheConfig`, cache data/file utilities, the shared `lru.Cache`, `gcs.Bucket` and `gcs.MinObject`, metrics and tracing handles, and `golang.org/x/sync/semaphore`. It is normally owned by `CacheHandler`, which inserts file-info entries before creating jobs and relies on manager invalidation during eviction.

## Risks and edge cases
The remove callback captures the object and bucket names from job creation; if object metadata is mutated by tests or callers after creation, the callback still uses the captured pointer fields and could remove the wrong key if mutable `MinObject.Name` were changed. The global semaphore is shared across jobs but first per-file parallel worker behavior is implemented inside `Job`, so manager-level limits depend on job code honoring the shared semaphore. `Destroy` snapshots jobs before invalidating, avoiding map iteration mutation hazards.

## Test signals
`downloader_test.go` verifies create/get/invalidate/destroy behavior, default permissions, repeated create reuse, concurrent `GetJob`, concurrent invalidation, and concurrent create versus invalidate. `jm_parallel_downloads_test.go` verifies manager-wide parallel download limits across jobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader.go -->
