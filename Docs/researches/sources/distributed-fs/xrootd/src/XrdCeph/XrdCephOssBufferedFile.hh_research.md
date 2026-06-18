# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssBufferedFile.hh

Purpose: declares the buffered file decorator used by `XrdCephOss::newFile()` when `ceph.usebuffer` is enabled.

Important APIs and types: `XrdCephOssBufferedFile : virtual public XrdCephOssFile` overrides the full `XrdOssDF` file API: open/close, sync and async read/write, `ReadV`, `ReadRaw`, `Fstat`, `Fsync`, and `Ftruncate`. `createBuffer()` returns a `std::unique_ptr<IXrdCephBufferAlg>` for raw or async buffer I/O.

State and persistence: stores the wrapped `XrdCephOssFile*` and deletes it in the destructor, so ownership is transferred to the decorator. It tracks per-thread read buffers in a map, a single write buffer, retry policy, buffer size/mode, path, flags, start time, and atomic byte counters.

Dependencies and integration: includes the Ceph OSS base classes and buffer interfaces. It relies on `m_fd` inherited from `XrdCephOssFile` after inner open.

Risks and test signals: ownership tests should ensure no double delete in decorator stacks. Concurrency tests should exercise `m_bufferReadAlgs` map access and read/write counters. Configuration tests should validate buffer sizes, maximum buffer counts, and `aio` versus `io` adapter selection.
