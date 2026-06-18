<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.cc

Purpose: Implements `XrdPosixXrootd`, the central POSIX-style client facade over XrdCl. It maps file, directory, metadata, filesystem, extended-attribute, checksum, and async I/O operations onto XRootD client APIs while preserving POSIX return conventions and errno/error-message behavior.

Important APIs/types/functions: Public methods implement `Access`, `Open`, `Close`, `Opendir`, `Closedir`, `Read`, `Pread`, `Write`, `Pwrite`, `Readv`, `Writev`, `VRead`, `Fstat`, `Stat`, `Statfs`, `Statvfs`, `Fsync`, `Ftruncate`, `Truncate`, `Mkdir`, `Rmdir`, `Rename`, `Unlink`, directory iteration/positioning, `Getxattr`, `QueryChksum`, `QueryOpaque`, `QueryError`, `StatRet`, `endPoint`, `myFD`, and async variants. Private helpers include `Fault()`, `OpenCache()`, and erasure-coding helpers `EcRename`, `EcStat`, and `EcUnlink`.

Control flow and state: Constructor performs one-time static initialization, optional `XRDPOSIX_CONFIG` client config loading, EC detection via `XRDCL_EC`, and descriptor-table initialization. `Open()` translates POSIX flags to XrdCl flags, handles stream descriptors, cache prepare/deferred opens, sync/async XrdCl open, descriptor assignment, and final stat collection. I/O paths look up and lock `XrdPosixFile` objects, enforce `int`-sized XrdCl I/O lengths, delegate through cache I/O (`XCio`), update offsets and size, and map failures through `ecMsg`. Admin operations use `XrdPosixAdmin` and notify cache for namespace mutations. EC helpers deep-locate file replicas and perform special stat/rename/unlink handling.

Dependencies/integration: Depends on XrdCl file/filesystem APIs, `XrdPosixFile`, `XrdPosixDir`, `XrdPosixAdmin`, `XrdPosixMap`, cache interfaces, config, stats, trace, and path translation. It is called by preload C wrappers and by the PSS proxy storage plugin.

Risks and test signals: High-risk areas include descriptor lifetime with async callbacks, cache deferral timing, errno vs negative-return conventions, read/write size overflow, `Writev()` short-write semantics, EC path behavior, and query-response ownership. Tests should cover open/create/truncate flag combinations, cache-hit and cache-miss stat/open behavior, async I/O close races, directory `StatRet`, EC redirector vs server paths, xattr/checksum queries, and preload interposition over local passthrough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.cc -->
