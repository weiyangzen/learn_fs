# sources/user-network-fs/gcsfuse/internal/cache/file/cache_handle.go

## Purpose
`cache_handle.go` implements per-open-object reads from the local file cache. A `CacheHandle` decides whether a read can be served from the local file, whether to wait for or trigger a downloader job, when to fall back to GCS, and how to update LRU recency and sequential/random read state.

## Important APIs, Types, And Functions
`CacheHandle` stores the local `*os.File`, optional `downloader.Job`, file-info LRU cache, `cacheFileForRangeRead`, and atomic sequential-read state (`isSequential`, `prevOffset`). Public methods are `NewCacheHandle`, `Read`, `IsSequential`, and `Close`. Important private helpers are `validateCacheHandle`, `shouldReadFromCache`, `getFileInfoData`, and `validateEntryInFileInfoCache`.

## Control Flow And State
`Read` validates the handle, rejects offsets outside object size, loads `FileInfo` without changing LRU order, and has a rapid/unfinalized-object guard that falls back when the requested offset is beyond the cached size. It determines whether the access remains sequential before updating `prevOffset`. Random reads do not wait for downloads; if range caching is disabled, they also avoid starting a job unless enough data is already cached.

The method clamps `requiredOffset` to object size. Sparse-mode reads delegate to `fileDownloadJob.HandleSparseRead` and require a cache hit; otherwise they fall back. Non-sparse reads with a job inspect job status, maybe call `Download(requiredOffset, waitForDownload)`, and then use `shouldReadFromCache` to ensure the job is valid and sufficiently advanced. If the job is nil, the file-info cache must show the whole file is present.

After readiness is established, `Read` calls `fileHandle.ReadAt`. EOF or unexpected EOF is accepted only when the number of bytes read equals the clamped requested length. Finally it validates the cache entry again with `changeCacheOrder=true` so the LRU marks the file recently used.

`IsSequential` returns false if the handle has already switched to random mode, if the current offset moves backward, or if the gap from previous offset exceeds `downloader.ReadChunkSize`. `Close` closes and nils the local file handle.

## State And Persistence Behavior
Persistent bytes live in a local cache file managed by downloader jobs and read through `ReadAt`. Metadata lives in the LRU `FileInfo` cache. The handle itself persists per-open state: sequential/random classification and last offset. Atomic fields allow concurrent reads to inspect/update read state, but broader file/cache coordination relies on downloader and cache concurrency guarantees.

## Dependencies And Integration Points
The file integrates `internal/cache/data`, `internal/cache/file/downloader`, `internal/cache/lru`, `internal/cache/util`, `logger`, and `internal/storage/gcs`. It is created by `CacheHandler.GetCacheHandle` and returned to higher filesystem read paths as the cache-backed reader.

## Risks And Edge Cases
Key risks include stale file-info cache entries after eviction, generation mismatch during reads, local file truncation causing short reads, random reads unintentionally starting downloads, and parallel-download mode changing wait behavior. Sparse mode assumes `fileDownloadJob` is non-nil before calling `HandleSparseRead`; malformed sparse handles could panic. The rapid unfinalized-object check is offset-only and comments acknowledge a possible edge around `offset+len(dst)`.

## Test Signals
`cache_handle_test.go` covers validation, sequential detection, job-status decisions, LRU recency changes, random/sequential reads, nil job behavior, file-info invalidation/generation mismatch, partial EOF handling, cache hit transitions, and parallel-download fallback behavior.
