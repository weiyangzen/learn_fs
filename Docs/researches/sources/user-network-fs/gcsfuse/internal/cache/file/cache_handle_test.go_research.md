# sources/user-network-fs/gcsfuse/internal/cache/file/cache_handle_test.go

## Purpose
This suite specifies `CacheHandle` read decisions against a fake storage bucket and local cache directory. It validates handle invariants, sequential/random classification, downloader job interactions, file-info cache validation, LRU recency updates, cache-hit reporting, and parallel-download fallback behavior.

## Important APIs, Types, And Functions
`cacheHandleTest` sets up fake storage, a test object, an LRU file-info cache, a local cache file, a downloader job, and a `CacheHandle`. Helpers `addTestFileInfoEntryInCache` and `verifyContentRead` populate metadata and verify local file contents/permissions.

Tests call private helpers (`validateCacheHandle`, `shouldReadFromCache`, `validateEntryInFileInfoCache`) and public methods (`Read`, `IsSequential`, `Close`). They also construct downloader jobs with different `cfg.FileCacheConfig` values to test parallel-download behavior.

## Control Flow And State
Validation tests assert nil file handles and nil file-info caches fail, while nil download jobs are allowed. Sequential tests show backward offsets and gaps larger than `downloader.ReadChunkSize` switch to random behavior.

`shouldReadFromCache` tests cover not-started jobs, failed/invalid jobs, completed jobs, offsets less than/equal/greater than required offset, and job-status errors. File-info validation tests cover present entries, missing entries, generation mismatch, insufficient offset, and whether lookups do or do not change LRU order.

Read tests cover offset beyond object size, nil file handle, nil job with cache miss/hit, random reads with range caching on/off, sequential reads that wait for download, LRU order updates after reads, sequential-to-random transition, destination buffers longer than remaining content, cache entry removal, generation change, repeated reads where the second is a cache hit, and parallel-download configurations that force fallback instead of waiting.

## State And Persistence Behavior
The suite creates real local cache files under `$HOME/cache/dir` and removes them in teardown. It uses fake storage for object content and downloader jobs to populate the cache file. State assertions include job status offsets, cache hit booleans, LRU eviction order, local file permissions, and byte-for-byte content checks.

## Dependencies And Integration Points
Tests integrate fake storage, mocked storage control client, GCS bucket/object APIs, downloader jobs, LRU cache, cache util permissions/path helpers, metrics noop, tracing noop, semaphores, random data, and testify suite/assertions.

## Risks And Edge Cases
The suite highlights failures caused by stale metadata, generation changes after a read begins, local file short reads, and random reads with parallel downloads. Sparse-mode paths and rapid unfinalized-object fallback are not covered in this file, despite code branches in `Read`.

## Test Signals
Coverage is strong for non-sparse cache handle behavior with real local I/O and fake GCS. It gives both unit-level private helper coverage and integration-style read/download coverage.
