<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/jm_parallel_downloads_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/jm_parallel_downloads_test.go

## Purpose
This testify test file verifies `JobManager` and `Job` parallel-download behavior under realistic fake-storage conditions. It focuses on object-size boundaries, O_DIRECT toggling, per-file parallelism, manager-wide `MaxParallelDownloads`, and simultaneous downloads of multiple objects.

## Important fixtures and APIs
Helper functions create random objects in fake buckets, configure fake storage, configure temporary LRU/cache directories, and initialize file-info cache entries. `TestParallelDownloads` is table-driven over object size, chunk size, per-file worker count, global max parallel downloads, subscribed offset, and O_DIRECT. `TestMultipleConcurrentDownloads` starts two jobs from one manager and waits for both subscribers.

## Control flow and state behavior
The setup inserts `data.FileInfo` for each object before creating jobs, matching the production expectation that downloader status updates mutate an existing LRU entry. Jobs are created through `JobManager.CreateJobIfNotExists`, subscribers are registered, and `Download(..., waitForDownload=false)` starts background downloads. Tests then wait on subscriber channels to observe enough downloaded bytes and inspect cache file content up to the notified offset.

## Dependencies and integration points
The tests use fake GCS storage and mocked storage layout, `lru.Cache`, `data.FileInfo`, no-op metrics/tracing, `cfg.FileCacheConfig`, and `util.GetDownloadPath`. They integrate manager-level semaphore configuration (`MaxParallelDownloads`) with `parallelDownloadObjectToFile` internals. O_DIRECT behavior is exercised by configuration, though actual fallback depends on platform file-opening semantics.

## Risks and edge cases
The tests use one-second timeouts and background goroutines, so slow environments can produce false failures. They verify content up to notified offsets, not necessarily full final completion or semaphore counts. The first per-file goroutine does not consume a global semaphore token by design; these tests exercise that indirectly but do not count actual concurrent readers.

## Test signals
Signals include downloading entire objects when object size exceeds worker-count times chunk size, capping ranges at object size, operating with O_DIRECT disabled, and allowing two concurrent object downloads under a manager-wide limit while both produce readable cached content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/jm_parallel_downloads_test.go -->
