<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.hh

Purpose: declares the large-buffer pool class used alongside `XrdBuffManager`.

Important APIs/types/functions: `XrdBuffXL::Init`, `Obtain`, `Recalc`, `Release`, `MaxSize`, `Trim`, `Stats`, constructor/destructor, private `BuckVec`, mutex `slotXL`, bucket vector, totals, page size, slots, max size, request count, and buffer count.

Control flow: the header exposes lifecycle/configuration, buffer acquisition/release, sizing, trimming, and stats methods. Actual bucket selection and memory allocation live in `XrdBuffXL.cc`.

State and persistence behavior: owns in-memory freelists and counters. No disk persistence. Destructor is intentionally empty because the global buffer manager is not expected to be deleted.

Dependencies: includes `XrdBuffer.hh` and `XrdSys/XrdSysPthread.hh` for `XrdSysMutex`. It grants no public direct bucket access.

Integration points: paired with `XrdBuffManager` and global `XrdGlobal::xlBuff`; configured by xrd `buffers maxbsz`; reported through buffer statistics; used for large read/write/vector I/O allocations.

Risks: class is designed as a singleton and is not copy-protected in the header. Consumers should not create multiple independent pools unless they understand memory accounting. `MaxSize()` is simple state, so callers must ensure `Init()` has run before relying on configured maximums.

Test signals: compile/link tests against `XrdBuffer`; API tests for max-size reporting before/after init; concurrent pool use tests through `XrdBuffManager`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffXL.hh -->
