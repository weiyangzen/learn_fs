## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCache.cc

Purpose: provides the POSIX cache-context adapter methods that forward to the process-global `XrdOucCache`.

Important APIs/functions: `CachePath`, `CacheQuery`, `Rmdir`, `Rename`, `Stat`, `Statistics`, `Truncate`, and `Unlink`.

Control flow: all methods dereference `XrdPosixGlobals::theCache`. `CachePath()` requests a local cache path with `ForPath`; `CacheQuery()` uses `ForAccess` when holding a cached file or `ForInfo` for status-only checks and maps `0` to fully cached, `-EREMOTE` to not fully cached, and other failures to `-1`.

State and persistence: the adapter does not maintain state but operates on the underlying cache, which may persist local cache entries and statistics. `Statistics()` copies cache counters from `theCache->Statistics`.

Dependencies/integration: integrates `XrdOucCache`, `XrdOucCacheStats`, and the global cache set by configuration. Used by cache context manager initialization and cache-aware POSIX operations.

Risks: no null checks before using `theCache`; callers must ensure cache initialization. Return-value semantics mix negative errno-style cache values with POSIX-style `-1`. Some operations may be unsupported by a cache implementation despite being exposed here.

Test signals: cache enabled/disabled setup; `LocalFilePath()` return mapping for full, remote/incomplete, and error states; cache stat/unlink/rename behavior; statistics population.
