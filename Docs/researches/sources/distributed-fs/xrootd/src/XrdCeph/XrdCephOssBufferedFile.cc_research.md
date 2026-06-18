# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssBufferedFile.cc

Purpose: implements a decorator around `XrdCephOssFile` that adds buffered read/write behavior and summary metrics while delegating metadata and raw operations to the wrapped file object.

Important APIs: `Open()` opens the inner file, stores fd/path/flags, and starts a timer. `Close()` flushes write cache when needed, logs aggregate counters and elapsed time, then closes the inner file. `Read(void*, off_t, size_t)` maintains one read buffer algorithm per calling thread, retries `-EBUSY`, and falls back to the inner file if a new buffer cannot be created. `Read(XrdSfsAio*)`, `Write()`, and `Write(XrdSfsAio*)` route through `IXrdCephBufferAlg`. `ReadV`, `ReadRaw`, `Fstat`, `Fsync`, and `Ftruncate` mostly delegate.

Control flow: buffer creation is protected by `m_buf_mutex`. `createBuffer()` sizes buffers based on `m_bufsize` unless the per-file buffer count has reached `m_maxCountReadBuffers`, then creates a smaller 1 MiB buffer. It selects `CephIOAdapterAIORaw` for `aio` mode or `CephIOAdapterRaw` for `io` mode; invalid modes close the inner file and return null.

State and persistence: maintains one write buffer (`m_bufferAlg`), a map of per-thread read buffers, file flags/path, counters, and timing. Persistent writes are flushed through the buffer algorithm before close.

Dependencies and integration: depends on buffer interfaces and simple implementations under `XrdCephBuffers`, `XrdSfsAio`, `XrdCephPosix`, and the parent `XrdCephOss` pread flag.

Risks and test signals: tests should cover close-after-flush failure, concurrent reads from multiple threads, maximum buffer behavior, invalid `bufferiomode`, retry exhaustion, and write-cache flush ordering. AIO read creation does not check `createBuffer()` for null before dereference, so invalid mode or allocation failure is a notable crash risk.
