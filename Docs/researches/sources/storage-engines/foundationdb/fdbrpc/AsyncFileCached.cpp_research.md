# sources/storage-engines/foundationdb/fdbrpc/AsyncFileCached.cpp

Purpose: implementation of cached asynchronous file access. It maintains global/non-simulated and per-simulated-machine page caches, routes reads/writes through cached pages, supports zero-copy page reads, truncation, flushing, and cleanup.

Important APIs and functions: global caches `pc4k`, `pc64k`, and `simulatorPageCaches`; `EvictablePage::~EvictablePage`; `AsyncFileCached::openFiles`; `open_impl`; templated `read_write_impl<writing>`; `readZeroCopy`; `releaseZeroCopy`; `changeFileSize`; `flush`; `quiesce`; and destructor.

Control flow: open chooses a 4K or 64K `EvictablePageCache` based on flags and simulation context. Reads/writes split requests by page, create or hit `AFCPage` objects, and wait for outstanding page futures. Truncation flushes a partial terminal page, removes pages beyond new EOF using either targeted lookups or map scan, then truncates the underlying file. Flush walks `flushable` pages until all are written.

State and persistence behavior: cached pages are in-memory; durable persistence remains with the underlying uncached file after flush/truncate. Length and previous length track file size locally. Orphaned zero-copy pages are reference-counted by data pointer after eviction.

Dependencies and integration points: depends on Flow futures, page cache classes from `AsyncFileCached.h`, `IAsyncFile`, network simulation state, knobs, and aligned allocation helpers.

Risks: comments note read/write path assumptions about no waits before `prevLength` update. Zero-copy requires aligned full-page reads within file length. Destructor aborts if any page cannot be evicted.

Test signals: no direct tests in this subset; behavior is likely covered by broader file-system and simulation tests.
