# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterAIORaw.cc

Purpose: implements a Ceph IO adapter using XrdCeph asynchronous POSIX calls internally, but waits synchronously for completion before returning.

Important APIs/types/functions: local callbacks `aioReadCallback` and `aioWriteCallback`; `CephBufSfsAio` constructor, `doneRead`, `doneWrite`; `CephIOAdapterAIORaw` constructor/destructor, `read`, and `write`.

Control flow: `read`/`write` obtain the raw buffer, create a `CephBufSfsAio`, fill `sfsAio` buffer/offset/length, call `ceph_aio_read` or `ceph_aio_write`, then wait on the condition variable until callback marks done. On read success, buffer length, starting offset, and validity are updated.

State and persistence: holds non-owned buffer pointer, file descriptor, and timing/byte/request counters. Data persistence happens through Ceph writes, not this class.

Dependencies and integration points: depends on `XrdCephPosix.hh` async APIs, `XrdSfsAio`, `Timer_ns`, and `IXrdCephBufferData`. Used as an `ICephIOAdapter`.

Risks: `CephBufSfsAio` constructs `unique_lock` locked; callbacks unlock it from another thread, which is not valid ownership for `std::unique_lock` and is a serious concurrency risk. Counters add negative `rc` values after write failures. Timing units mix nanoseconds and milliseconds in atomic fields/logging.

Test signals: async read/write success, submit failure, callback error result, race/deadlock tests under thread sanitizer, zero-byte operations, and buffer metadata updates after read.
