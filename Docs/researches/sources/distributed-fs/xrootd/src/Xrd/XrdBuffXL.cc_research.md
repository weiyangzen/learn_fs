<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.cc

Purpose: implements `XrdBuffXL`, the large-buffer extension pool used when requested buffers exceed the normal `XrdBuffManager` maximum. It caches power-of-two-aligned buffers from roughly 4 MiB up to a configurable cap, with a hard 1 GiB maximum.

Important APIs/types/functions: constructor, `Init(int maxMSZ)`, `Obtain(int sz)`, `Recalc(int sz)`, `Release(XrdBuffer*)`, `Stats(char*,int,int)`, and `Trim()`. Local constants define `maxBuffSz`, `iniBuffSz`, `minBuffSz`, `minBShift`, and `isBigBuff`.

Control flow: `Init()` resets any existing bucket vector, clamps the max size, rounds it to power-of-two bucket coverage, and allocates `BuckVec` slots. `Obtain()` validates size, maps it to a bucket index, pops an existing buffer under `slotXL`, or allocates page-aligned memory with `posix_memalign` and wraps it in `XrdBuffer` with the big-buffer marker in `bindex`. `Release()` pushes the buffer back to its bucket. `Trim()` frees excess cached buffers when free count exceeds recent requests, then resets per-bucket request counters.

State and persistence behavior: process-memory state only: bucket freelists, per-bucket buffer/request counts, total allocated bytes, total requests, total buffers, max size, and slot count. It intentionally is singleton-like and never deleted in normal operation.

Dependencies: uses `XrdBuffer`, `XrdSysMutex`, `XrdOucUtils::Log2`, page size from `getpagesize()`, `posix_memalign`, and standard allocation/free. It is referenced through `XrdGlobal::xlBuff` from `XrdBuffer.cc` and configured by `XrdConfig::xbuf`.

Integration points: `XrdBuffManager::Obtain()` delegates oversized requests to this pool; `XrdBuffManager::Release()` sends marked buffers back here; stats are embedded under normal buffer stats; reshape trims this pool after normal pool pressure handling.

Risks: all callers must release buffers to the correct manager; the `isBigBuff` marker protects this but depends on `bindex` integrity. `Init()` can delete and replace buckets without freeing buffers currently checked out or cached in old buckets, so reconfiguration timing matters. `Trim()` frees while holding the mutex, which can extend lock hold time for many large buffers.

Test signals: allocation/release tests across bucket boundaries and max-size rejection; `Recalc()` expected-size tests; stats tests after obtain/release/trim; concurrency stress for obtain/release; config tests for `buffers maxbsz`; memory-pressure tests that verify trim returns large buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.cc -->
