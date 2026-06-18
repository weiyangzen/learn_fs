## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFile.cc

Purpose: implements the core remote file object, combining descriptor-object behavior, `XrdOucCacheIO` backend methods, `XrdCl::File` operations, async response handling, cache attachment, stat caching, and delayed destruction.

Important APIs/functions: constructor/destructor, `DelayedDestroy` thread and enqueue overload, `Close`, `Fcntl`, `Finalize`, `Fstat`, `HandleResponse` for async open, `Location`, pgread/pgwrite sync and async overloads, `Read`, `ReadV`, `Stat`, `Sync`, `Trunc`, and `Write`.

Control flow: construction stores origin/cache paths, applies name-to-name translation when a cache exists, and sets cache options. `Finalize()` initializes current offset, stats an open file or uses deferred `PrepIO`, then attaches cache if configured. I/O methods take a reference, call the relevant `XrdCl::File` operation, unref on synchronous completion, or hand a response handler the responsibility to unref. Read can auto-convert to pgread when configured. `DelayedDestroy()` runs in a background thread and retries closing files whose reference count or remote close status prevents immediate deletion.

State and persistence: per-file state includes `XCio`, optional deferred `PrepIO`, `clFile`, size/timestamps/mode/inode/rdev, current offset, callback/linked-list union fields, origin/cache path/location, cache options, stream flag, and static delayed-destroy queues. No direct durable writes except remote file/cache I/O.

Dependencies/integration: integrates `XrdCl::File`, cache interfaces, `XrdPosixConfig`, `XrdPosixFileRH`, `XrdPosixPrepIO`, stats/trace, name mapping, and global delayed-destroy/cache settings.

Risks: heavy global/static lifetime complexity. Union reuse for current offset/callback/next pointer and cache option/try count requires strict phase separation. Delayed destroy can leak into `ddLost` after retry exhaustion. Size/block calculations and stat field population must match admin stat behavior. Async paths rely on balanced `Ref()`/`unRef()`.

Test signals: sync and async read/write/readv/pgread/pgwrite; close during active I/O; deferred open/cache attach; failed close retry and lost counters; auto pgread mode; stat extended metadata; location refresh property.
