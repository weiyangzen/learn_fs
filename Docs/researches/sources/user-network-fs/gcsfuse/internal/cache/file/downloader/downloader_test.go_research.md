<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader_test.go

## Purpose
This ogletest suite validates `JobManager` behavior and provides shared setup for many downloader tests. It creates fake GCS storage, seeded objects, cache directories, LRU file-info entries, default `Job` instances, and cleanup logic used by job, parallel, and sparse downloader suites.

## Important fixtures and APIs
`downloaderTest` holds `defaultFileCacheConfig`, a current `Job`, fake `gcs.Bucket`, current object metadata, LRU cache, fake storage, `FileSpec`, and `JobManager`. `setupHelper` enables invariant checks, resets the cache directory, creates fake storage with a mocked storage-layout call, initializes a default job test object, and constructs a `JobManager`. `waitForCrcCheckToBeCompleted` polls terminal job status because subscriber notification can occur before final CRC validation.

## Control flow and state behavior
The tests cover `JobManager.CreateJobIfNotExists`, `GetJob`, `InvalidateAndRemoveJob`, and `Destroy`. They assert that create deduplicates by bucket/object path, populates download paths and permissions, and stores jobs under manager lock. Invalidation tests start downloads, call manager invalidation, and expect the job status to become `Invalid` and the manager map entry to disappear. Destroy snapshots and invalidates multiple jobs in different states.

## Dependencies and integration points
The suite uses fake storage (`storage.NewFakeStorageWithMockClient`), `storageutil.CreateObjects`, cache data types, `lru.Cache`, cache utility path helpers, no-op metrics/tracing, and integration cleanup operations. It is coupled to the `Job` test helper in `job_test.go` via `initJobTest`, so the manager tests also depend on file-info cache setup.

## Risks and edge cases
Concurrency tests check that manager locking prevents duplicate reads and deletion races but do not assert exact callback counts for manager removal. The global `cacheDir` under `$HOME/cache/dir` is shared across tests, so parallel test execution outside the suite's expectations could conflict. `TearDown` invalidates both the current job and manager, which is correct but can mask bugs where callbacks are already removed.

## Test signals
The file verifies non-existing and existing create/get paths, default file/dir permissions, concurrent `GetJob`, invalidating absent and present jobs, concurrent invalidation, destroying multiple jobs, and concurrent create/invalidate calls. It is a primary signal for the `JobManager` locking and callback-removal contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader_test.go -->
