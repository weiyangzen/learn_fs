<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler_test.go

## Purpose
This test file validates `CacheHandler`, the file-cache layer that turns GCS objects into local cache handles and coordinates file-info LRU entries, downloader jobs, local cache files, regex filtering, eviction cleanup, invalidation, sparse-mode setup, and cache destruction. It is the main integration-style test surface between `internal/cache/file`, `internal/cache/file/downloader`, `internal/cache/lru`, fake GCS storage, and cache filesystem utilities.

## Important fixtures and APIs
`cacheHandlerTestArgs` bundles the fake bucket, object metadata, LRU cache, `JobManager`, `CacheHandler`, local download path, and cache key. `initializeCacheHandlerTestArgs` creates fake storage, a test object, a volume-block-aware LRU cache, a `JobManager`, and a `CacheHandler` initialized with regex and sparse settings from `cfg.FileCacheConfig`. Helpers such as `createObject`, `addTestFileInfoEntryInCache`, `getDownloadJobForTestObject`, `isEntryInFileInfoCache`, and `doesFileExist` keep tests focused on externally visible cache behavior.

## Control flow and state behavior
The tests exercise the lifecycle from `GetCacheHandle` through file-info insertion, job creation, reads, eviction, and invalidation. Existing file-info entries are reused when generation and job state match; generation changes, failed jobs, invalid jobs, or missing jobs for incomplete files force cleanup and replacement. Eviction paths call `cleanUpEvictedFile`, which invalidates the download job, removes it from `JobManager`, truncates/removes the local file, and tolerates already-missing cache files. Regex tests show include filtering is applied before exclude precedence, and a file that matches both include and exclude is rejected. Range-read tests assert that non-random reads can create cache handles, while random range reads may bypass file caching unless full-object caching is requested.

## Dependencies and integration points
The file depends on fake storage and a mocked storage-control client, `data.FileInfo`, `downloader.JobManager`, `lru.Cache`, cache utility path creation and truncation, volume block size discovery, metrics/tracing no-op handles, and integration-test filesystem cleanup utilities. It implicitly documents the contract between `CacheHandler` and `CacheHandle.Read`: non-parallel sequential cache reads can synchronously wait for needed offsets, while parallel mode may return read errors when foreground reads do not wait the same way.

## Risks and edge cases
The most important risks covered are stale local state after GCS generation changes, deleted cache files with live LRU entries, eviction while downloads are in progress, concurrent `GetCacheHandle` and `InvalidateCache`, and size accounting that must use cache-volume block size. Some assertions use sleeps or timing-sensitive async job completion, which can be flaky if downloader cleanup timing changes. The destroy test has a likely copy/paste issue checking `job2` by asking for `minObject1` twice, so it may under-cover the second object job.

## Test signals
Coverage is broad: creation paths, generation replacement, failed/invalid job recovery, local-file deletion errors, eviction in parallel and non-parallel modes, regex include/exclude behavior, random-read bypasses, same-file and different-file concurrency, invalidation truncation of open file handles, full handler destroy, and block-size-sensitive LRU accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler_test.go -->
