<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.cc

Purpose: Implements deferred-open cache I/O for files whose open is postponed by an `XrdOucCache`. It allows the cache layer to accept a file object before the underlying `XrdCl::File` is opened and then performs the real open lazily on first I/O/stat/control operation.

Important APIs/types/functions: `Disable()` marks the deferred open as shut down using `-ESHUTDOWN`. `Init()` is the core lazy-open routine called by inline methods in `XrdPosixPrepIO.hh`. It locks the backing `XrdPosixFile`, avoids repeated opens, opens `fileP->clFile` with stored `clFlags`/`clMode`, maps open errors through `XrdPosixMap::Result`, updates global POSIX and cache statistics, calls `fileP->Stat(Status)` on success, and tells the cache `fileP->XCio->Update(*fileP)`.

Control flow and state: `openRC` caches the first open failure and prevents retries. `iCalls` tracks unexpected repeated use and logs as a power-of-two threshold grows. All entrypoints in the header call `Init()` before delegating to `XrdPosixFile`, and async variants complete callbacks with `openRC` if the open failed.

Dependencies/integration: Created by `OpenDefer()` in `XrdPosixXrootd.cc` when `theCache->Prepare()` asks for deferral. It integrates with `XrdOucCache`, `XrdOucCacheIOCB`, `XrdPosixObjGuard`, stats, trace, and auth-obfuscated debug logging.

Risks and test signals: Lazy open changes timing of errors and can surprise callers that expect `open()` to fail immediately. Tests should verify cache deferral success, deferred ENOENT/ELOOP behavior, async callback completion on failure, `Disable()` during shutdown, stats increments, and no deadlock while updating the cache I/O object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.cc -->
