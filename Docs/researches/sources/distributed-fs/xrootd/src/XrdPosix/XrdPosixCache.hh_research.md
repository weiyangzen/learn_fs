## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCache.hh

Purpose: declares `XrdPosixCache`, the adapter class exposed to cache context manager code for path lookup, status, metadata, mutation, and statistics operations.

Important APIs/types: `CachePath`, `CacheQuery`, `Rmdir`, `Rename`, `Stat`, `Statistics`, `Truncate`, `Unlink`; forward declaration of `XrdOucCacheStats`.

Control flow: header documents expected return contracts, including `CacheQuery()` full/partial/missing semantics and mutation method error values.

State and persistence: class has no fields; it is a stateless facade over a global cache implementation.

Dependencies/integration: the implementation depends on `XrdOucCache`; callers use this type as the POSIX cache interface. It is constructed statically in `XrdPosixConfig::initCCM()`.

Risks: documentation comments for some methods are copy-paste inaccurate, calling stat/statistics "Rename"; this can confuse implementers. Lack of explicit cache pointer in the type hides dependency on global initialization.

Test signals: API contract tests against a fake or instrumented cache; verify documented negative error cases, especially `Unlink()` returning `-EBUSY`, `-EAGAIN`, or `-errno`.
