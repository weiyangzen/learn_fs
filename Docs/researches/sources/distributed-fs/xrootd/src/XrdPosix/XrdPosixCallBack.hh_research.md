## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCallBack.hh

Purpose: defines callback interfaces for asynchronous open and asynchronous file I/O in the POSIX layer.

Important APIs/types: `XrdPosixCallBack` with pure virtual `Complete(int)`, and `XrdPosixCallBackIO` deriving from `XrdOucCacheIOCB` with pure virtual `Complete(ssize_t)`, private `Done(int)`, and `XrdPosixFile *theFile`.

Control flow: async open always returns `-1` with `errno=EINPROGRESS` on accepted work and later calls `Complete()` with the synchronous-style result. Async I/O completion is routed through `Done()`, which is friend-accessed by `XrdPosixExtra` and `XrdPosixXrootd`.

State and persistence: only stores a transient file pointer for outstanding I/O; no persistence.

Dependencies/integration: depends on `XrdOucCacheIOCB` and is consumed by `XrdPosixFile`, `XrdPosixFileRH`, `XrdPosixExtra`, and open paths.

Risks: documentation says callback objects are caller-owned after invocation; misuse can leak or double-delete callbacks. Immediate-error callbacks may run on the calling thread, so user locks must be reentrant if callback re-enters guarded code.

Test signals: accepted async open, rejected async open, immediate async I/O error, scheduled async I/O completion, callback deletion policy.
