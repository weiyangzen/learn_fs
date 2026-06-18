# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephBufferAlgSimple.cc

Purpose: implements a simple single-buffer read/write cache for XrdCeph files.

Important APIs/types/functions: constructor/destructor; `read_aio`, `write_aio` translate AIO to synchronous operations and complete callbacks; `read` handles cache hits/fills and large-read bypass; `write` buffers sequential writes; `flushWriteCache` writes pending data through the adapter; `rawRead/rawWrite` are unimplemented.

Control flow: `read` locks a recursive mutex, bypasses the cache for reads at least as large as capacity, otherwise loops until requested bytes are satisfied or EOF, loading the cache via `m_cephio->read` when the current offset is outside cached data. `write` requires sequential offsets once data is buffered, writes chunks into the buffer, flushes when full, and leaves partial data cached until explicit flush. AIO methods call sync methods and then `doneRead`/`doneWrite`.

State and persistence: owns buffer data and IO adapter via `unique_ptr`, tracks fd, striperless flag, cache starting offset/length, recursive mutex, and byte stats. Dirty write data is only persisted when the buffer fills or `flushWriteCache` is called.

Dependencies and integration points: depends on `IXrdCephBufferData`, `ICephIOAdapter`, XrdCeph POSIX bypass reads, and XrdSfsAio. Intended for `XrdCephOssBufferedFile`.

Risks: callers must flush partial writes before close to avoid data loss. Large-read bypass uses direct `ceph_posix_maybestriper_pread` instead of the adapter, bypassing adapter instrumentation/policy. `volatile void *` casts and recursive mutex indicate interface friction. Non-sequential writes return `-EINVAL`.

Test signals: cache hit/miss, read across buffer boundary, EOF short reads, large-read bypass, sequential writes with full/partial flush, non-sequential write error, AIO completion, and concurrent access serialization.
