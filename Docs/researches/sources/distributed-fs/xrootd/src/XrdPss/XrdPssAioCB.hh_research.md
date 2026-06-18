<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.hh

Purpose: Declares `XrdPssAioCB`, the callback adapter used by PSS asynchronous I/O. It bridges `XrdPosixCallBackIO` completions to `XrdSfsAio` server callbacks and provides a small object pool.

Important APIs/types/functions: `Alloc()` creates or reuses a callback for a given `XrdSfsAio`, operation direction, and page-read/write flag. `Complete()` is the virtual callback invoked by POSIX async operations. `Recycle()` returns the object to the pool. `SetMax()` controls maximum cached callbacks. Public `csVec` carries page I/O checksum vectors.

Control flow and state: Static pool state is guarded by `myMutex`. Active state includes a union of `theAIOP`/`next`, booleans `isWrite` and `isPGrw`, and the checksum vector. Constructor/destructor are private to force allocation through `Alloc()`.

Dependencies/integration: Includes `XrdPosixCallBack.hh` and `XrdSysPthread.hh`; forward-declares `XrdSfsAio`. It is owned by async PSS methods.

Risks and test signals: Misuse outside `Alloc()` is prevented, but lifetime correctness depends on every completion calling `Recycle()` exactly once. Tests should include high-concurrency async operations, pool max changes, page checksum vector reuse after recycle, and no use-after-free when callbacks complete after file close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.hh -->
