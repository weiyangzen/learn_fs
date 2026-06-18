# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephPosix.hh

Purpose: declares the Ceph POSIX facade used by the OSS, buffering, readv, bulk read, and xattr layers.

Important APIs: exposes setup functions (`ceph_posix_set_defaults`, `ceph_posix_disconnect_all`, `ceph_posix_set_logfunc`), file operations (`open`, `close`, seek, read, pread variants, write, pwrite, AIO read/write, fstat, stat, fsync, fcntl, truncate, unlink), readv helpers, xattr operations, stats, and directory iteration. It also declares `ceph_posix_maybestriper_pread()` for code that wants direct-object reads with optional striper fallback.

Important types: `CephFile` stores parsed object name, pool, user, stripe count, stripe unit, and object size. `CephFileRef` extends it with flags, mode, offset, stats mutex, byte counters, operation counters, and AIO timing fields. `AioCB` is the callback signature for XRootD AIO completion.

State and persistence: the header describes transient file-reference state, not persistent storage. The implementation persists through Ceph object and xattr operations.

Dependencies and integration: includes `XrdOucEnv`, `XrdSysXAttr`, `XrdSysPthread`, and `XrdOucIOVec`. `LOGCEPH` is a simple logging macro used by buffer and readv code.

Risks and test signals: interface tests should cover return-value conventions and negative errno mapping. Because `CephFileRef` contains mutable stats protected by `XrdSysMutex`, concurrent AIO and close tests are especially important.
