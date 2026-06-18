<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_cache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/read_cache_test.go

Purpose: integration coverage for the file read cache under mounted gcsfuse. It validates when cache files are populated, reused, evicted, invalidated, rebuilt for new object generations, or intentionally bypassed.

Important APIs/types/functions: ogletest suites `FileCacheTest`, `FileCacheWithCacheForRangeRead`, `FileCacheIsDisabledWithCacheDirAndZeroMaxSize`, and `FileCacheDestroyTest`; helpers `generateRandomString`, `sequentialReadShouldPopulateCache`, `cacheFilePermissionTest`, `writeShouldNotPopulateCache`, `sequentialToRandomReadShouldPopulateCache`, and `excludedFileShouldNotPopulateCache`. Config knobs under test include `cfg.FileCacheConfig.MaxSizeMb`, `CacheFileForRangeRead`, `EnableCrc`, `ExcludeRegex`, and `CacheDir`.

Control flow: setup enables implicit directories, noop metrics/tracing, and a cache directory under `$HOME/cache-dir/file-cache`. Tests create fake GCS objects, read through `mntDir` using `O_DIRECT` or `os.ReadFile`, then inspect `util.GetDownloadPath` on disk. Sequential reads populate the cache, random reads populate only when `CacheFileForRangeRead` is true, writes alone do not populate, and sync after dirtying a cached file refreshes cached content.

State and persistence behavior: persistent signals are on-disk cache files and fake GCS objects. The suite validates cache permissions, max-size rejection for oversized files, LRU promotion on read, eviction when full, range-read asynchronous population, local edits to cache files being served on later reads, and cache survival across unmount. Deletes and renames remove the old cached object path, including nested objects when a directory is renamed.

Dependencies and integration points: depends on the fs test harness, fake bucket object creation, `internal/cache/util` path helpers and size constants, direct I/O behavior, local filesystem cache state, metrics/tracing noops, and the server file-cache handler built from `ServerConfig.NewConfig`.

Risks: tests use global `CacheDir` and `FileCacheDir`, so teardown correctness is important for isolation. Random data and asynchronous range-read cache population can expose timing sensitivity. `O_DIRECT` behavior is platform-sensitive. The `ModifyFileInCacheAndThenReadShouldGiveModifiedData` case intentionally demonstrates that cache trust is strong enough for local cache corruption to affect reads.

Test signals: covers sequential/range/random read cache policy, exclude regex, disabled cache behavior, file-size boundary at equal/greater than cache size, LRU and eviction, stale cache handle behavior after cache-file deletion, invalidation on unlink/rename/renamed directory, concurrent reads from one handle, sync/write correctness, generation rebuild after stat-cache expiry, and unmount persistence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_cache_test.go -->
