# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioBuff.cc

Purpose: implements the base async-I/O buffer object used by normal xrootd AIO tasks. It connects an `XrdSfsAio` completion object to an `XrdXrootdAioTask`, owns a temporary `XrdBuffer` segment from the global `XrdXrootd::BPool`, and returns completed operations to the task.

Important APIs and functions: `XrdXrootdAioBuff::Alloc()` obtains a protocol segment-sized buffer, reuses an object from a static free queue when possible, initializes `sfsAio.aio_buf`, `aio_nbytes`, `cksVec`, `reqP`, and `buffP`, then increments the protocol AIO counter with `aioUpdate(1)`. `doneRead()` and `doneWrite()` both call `reqP->Completed(this)`. `Recycle()` decrements the protocol AIO counter, releases the buffer back to `BPool`, and either caches the object on a mutex-protected free list or deletes it once `maxKeep` is reached.

Control flow and state: the file maintains process-local static state `fqFirst`, `numFree`, and `fqMutex`; only AIO objects are cached, not data buffers. The callback path is intentionally short: filesystem completion calls `doneRead()` or `doneWrite()`, which enqueues the buffer in the request; request code later calls `Recycle()`.

Dependencies and integration: depends on `XrdBuffer`, `XrdSfsAio`, `XrdXrootdAioTask`, `XrdXrootdProtocol`, global `BPool`, and tracing. It is the normal buffer class beneath `XrdXrootdNormAio`-style file/link transfers; page read/write uses the derived `XrdXrootdAioPgrw`.

Risks and test signals: correctness depends on balanced `aioUpdate()` calls and exactly one `Recycle()` per allocation. Races concentrate around the free queue and around callbacks arriving after a task goes offline. Useful tests include buffer-pool exhaustion, concurrent completions, delayed completions after client disconnect, and tracing/counter assertions that active AIO counts return to zero.
