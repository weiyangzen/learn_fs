# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFile.hh

## Purpose
Defines the file descriptor wrapper used by `XrdOssStats::FileSystem` to count and time file-level OSS operations.

## Important APIs and control flow
`File` inherits `XrdOssWrapDF`, owns the wrapped `XrdOssDF`, and forwards calls through `wrapDF`. Most methods construct a `FileSystem::OpTimer` around the operation: `Open`, `Fchmod`, `Fstat`, `Ftruncate`, `pgRead`, `pgWrite`, scalar `Read` variants, scalar `Write`, and `WriteV`. `ReadV()` is manually timed so it can also count vector segments in `m_readv_segs`.

## State, dependencies, and integration
The wrapper holds `m_wrapped`, a logger reference, an unused `m_client` pointer, and a parent `FileSystem` reference. It directly updates the parent's atomic counters/timers through friendship. It depends on `XrdOssWrapper`, `XrdSysError`, and the filesystem header.

## Risks and test signals
`ReadV()` appears to add slow readv duration to `m_times.m_readv` rather than `m_slow_times.m_readv`, unlike `OpTimer`; this is a likely metrics bug. The `m_client` member is not initialized by the constructor. Tests should compare counters for every file operation, check vector segment accounting, and verify slow-readv timing lands in the expected JSON field.
