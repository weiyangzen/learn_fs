# sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler.go

## Purpose
`cache_handler.go` owns creation, lookup, invalidation, and cleanup of file-cache entries. It coordinates the file-info LRU cache, downloader job manager, local cache files, include/exclude regex policy, sparse-mode metadata, and cache-handle construction under a lock.

## Important APIs, Types, And Functions
`CacheHandler` stores the file-info cache, downloader `JobManager`, cache directory, file/dir permissions, a `locker.Locker`, compiled include/exclude regexes, sparse-mode flag, and volume block size. Public functions and methods include `NewCacheHandler`, `GetCacheHandle`, `InvalidateCache`, `Destroy`, and `shouldExcludeFromCache`. Private helpers include `compileRegex`, `createLocalFileReadHandle`, `cleanUpEvictedFile`, and `addFileInfoEntryAndCreateDownloadJob`.

## Control Flow And State
`NewCacheHandler` compiles regex filters and initializes the locker. Invalid regex strings are logged and ignored. `createLocalFileReadHandle` maps bucket/object names to a cache path and opens/creates it read-only with configured permissions.

`cleanUpEvictedFile` validates the cache key, invalidates/removes the corresponding download job, and truncates/removes the local cache file, ignoring missing files. `addFileInfoEntryAndCreateDownloadJob` builds the file-info key, checks for an existing entry, verifies the local file still exists, invalidates old entries when generation differs or the job is failed/invalid/missing before full download, inserts new `FileInfo`, creates a downloader job, and cleans up any LRU evictions. In sparse mode it sets `Offset` to `MaxUint64` and initializes `DownloadedChunks` with the job manager's download chunk size.

`GetCacheHandle` locks the handler, applies regex exclusion, skips cache creation for non-sparse random reads when range caching is disabled and no entry exists, ensures file-info/job state, creates a local file read handle, and returns a `CacheHandle` with the current job. `InvalidateCache` erases a specific entry and performs cleanup. `Destroy` invalidates all jobs through the job manager.

## State And Persistence Behavior
The handler mutates in-memory LRU metadata and downloader job state, and it creates/truncates/removes local cache files under `cacheDir`. LRU evictions trigger cleanup of both local file and job. Sparse mode persists partial object bytes in the same local file but accounts downloaded chunks through `FileInfo.DownloadedChunks`.

## Dependencies And Integration Points
The file integrates `data.FileInfo`/`FileSpec`, downloader `JobManager`, LRU cache, cache util path and file helpers, `locker`, `logger`, regex/path standard libraries, and `gcs.Bucket`/`MinObject`. It is the factory for `CacheHandle` and the invalidation hook for filesystem changes/unmount.

## Risks And Edge Cases
Correctness depends on holding `chr.mu` around cache/job/file transitions. Existing file-info entries with missing local files cause errors instead of self-healing in that path. Generation comparison cannot rely on monotonicity, so any mismatch invalidates. Regex exclusion uses `path.Join(bucket.Name(), bucket.GCSName(object))`, so policy patterns must match that joined form. Sparse random reads always create handles even when range caching is disabled.

## Test Signals
No `cache_handler_test.go` is part of this work item, but `cache_handle_test.go` and data tests cover consumers and metadata. Direct risks around regex filtering, eviction cleanup, sparse initialization, and missing-file behavior should be covered by separate cache-handler tests elsewhere.
