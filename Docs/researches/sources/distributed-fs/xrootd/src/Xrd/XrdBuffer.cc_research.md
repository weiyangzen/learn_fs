<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.cc

Purpose: implements the normal server buffer pool, including fixed power-of-two buckets, aligned allocation, recycling, memory accounting, XML-like stats, and a background reshaper thread that trims cached buffers under memory pressure or periodic review.

Important APIs/types/functions: external thread entry `XrdReshaper`, `XrdBuffManager` constructor/destructor, `Init()`, `Obtain(int)`, `Recalc(int)`, `Release(XrdBuffer*)`, `Reshape()`, `Set(int,int)`, and `Stats(char*,int,int)`.

Control flow: `Init()` starts a reshaper thread. `Obtain()` rejects non-positive sizes, delegates oversized requests to `xlBuff`, computes a bucket by `Log2`, pops a cached buffer under the condition-variable lock, or allocates aligned memory and updates counters; if allocation pushes total memory over `maxalo`, it signals the reshaper. `Release()` returns normal buffers to bucket freelists and delegates large marked buffers to `xlBuff`. `Reshape()` loops forever, waiting on pressure or interval, computing a target profile from recent request counts, freeing surplus buffers from largest buckets down to an 80% target, resetting counters, and trimming `xlBuff`.

State and persistence behavior: process-memory-only cache. Persistent effects are indirect: buffer limits affect daemon throughput and memory footprint. State includes bucket freelists, counts, request history, total allocated bytes, target max allocation, reshape interval, reshape-in-progress flag, total adjustments, and global `XrdGlobal::xlBuff`.

Dependencies: `XrdOucUtils::Log2`, `XrdSysError`, `XrdSysThread`, `XrdSysCondVar`, `XrdSysTimer`, `XrdTrace`, `XrdBuffXL`, page size and `sysconf(_SC_PHYS_PAGES)`, `posix_memalign`.

Integration points: exported globally as `XrdGlobal::BuffPool` and passed into `XrdProtocol_Config`. Protocol implementations obtain transient I/O buffers through this manager. `XrdConfig::xbuf` changes memory/reshape settings, and `XrdStats` reports `Stats()`.

Risks: the reshaper thread never exits, matching daemon lifetime assumptions. Memory accounting can drift if external code tampers with `XrdBuffer` internals, though friendship limits access. `Obtain()` uses `posix_memalign` alignment of `mk` for sub-page buffers and page size otherwise; platform-specific allocation behavior matters. Under high churn, freeing buffers while reshaping can race only through the lock, so lock contention is the main performance risk.

Test signals: bucket sizing tests for `Obtain()`/`Recalc()`; release/reuse tests; oversized delegation tests to `XrdBuffXL`; stats formatting tests; reshape tests with low `maxalo`; stress tests with many threads; startup test ensuring reshaper thread creation failures are logged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.cc -->
