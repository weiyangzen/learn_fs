# sources/distributed-fs/xrootd/src/XrdThrottle/XrdOssThrottleFile.cc

Purpose: implements the newer OSS-layer throttle wrapper, allowing throttling after OFS authorization has made the authenticated user available.

Important APIs/types/functions: anonymous `File` derives from `XrdOssWrapDF` and wraps open/close, reads, writes, paged reads/writes, vector reads, and AIO shims. Anonymous `FileSystem` derives from `XrdOssWrapper`, configures `XrdThrottleManager`, and wraps `newFile()`. Exported `XrdOssAddStorageSystem2()` is the OSS plugin factory with `XrdVERSIONINFO`.

Control flow: the factory constructs `FileSystem`, calls `Configure()`, sets environment flag `XrdOssThrottle=1`, and returns it. `FileSystem` initializes the manager, loads configuration, applies config, and optionally attaches g-stream monitoring. Each wrapped file derives user info from `env.secEnv()` on open, checks open/connection limits, delegates to the wrapped OSS file, and closes manager accounting on failure or close. I/O methods call `DoThrottle()`, which applies data/IOPS shares, starts an RAII I/O timer, fails with `-EMFILE` when concurrency wait times out, and then invokes the wrapped operation.

State and persistence: `FileSystem` owns the wrapped OSS, log, trace, and throttle manager. Each `File` stores wrapped file ownership, user string, hashed UID, and references to manager/trace/log. Environment flag persists in `XrdOucEnv` to prevent OFS-layer double stacking.

Dependencies and integration: depends on XrdOss wrapper APIs, `XrdOucGatherConf`, `XrdSfsAio`, `XrdThrottleConfig`, `XrdThrottleManager`, `XrdThrottleTrace`, and XRootD plugin ABI. It complements the older OFS-layer wrapper in `XrdThrottleFileSystemConfig.cc`.

Risks: `Close()` always calls `CloseFile()` even if open accounting did not succeed or close is repeated. AIO is forced synchronous by doing the operation and then calling done callbacks. `getFD()` and mmap are disabled, which may affect sendfile/mmap optimizations. `DoThrottle()` returns `int` even when wrapping `ssize_t` operations.

Test signals: OSS plugin load, no double OFS stacking, open-limit failures, close rollback on open failure, read/write throttling, AIO callback behavior, g-stream monitoring, and sendfile/mmap expectations.
