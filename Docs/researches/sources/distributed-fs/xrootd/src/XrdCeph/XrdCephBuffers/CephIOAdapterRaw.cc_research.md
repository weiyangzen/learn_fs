# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterRaw.cc

Purpose: implements the synchronous raw Ceph IO adapter using XrdCeph POSIX-style pread/pwrite functions.

Important APIs/types/functions: constructor stores non-owned buffer and fd; destructor logs aggregate stats; `write` calls `ceph_posix_pwrite`; `read` calls `ceph_posix_maybestriper_pread`.

Control flow: `write` validates raw const buffer, times the pwrite, updates write counters on success, and returns the byte count/error. `read` validates mutable raw buffer, performs possibly striperless pread, logs errors, updates counters, and marks the buffer length/starting offset/valid on success.

State and persistence: adapter accumulates runtime counters and writes through to Ceph for persistence. It does not own the buffer or fd.

Dependencies and integration points: depends on `XrdCephPosix.hh`, `IXrdCephBufferData`, and `BUFLOG`. Used by `XrdCephBufferAlgSimple`.

Risks: no capacity check before reading into the buffer; callers must keep `count <= capacity`. Destructor write-speed guard checks `m_stats_read_timer` instead of `m_stats_write_timer`, which can suppress or skew write speed. Atomic counters are logged directly and unit math appears inconsistent.

Test signals: null buffer returns `-EINVAL`, successful read metadata, read error logging, pwrite success/error, striperless flag behavior, and destructor stats with read-only/write-only workloads.
