## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCallBack.cc

Purpose: implements completion glue for asynchronous POSIX I/O callbacks.

Important APIs/functions: `XrdPosixCallBackIO::Done(int result)`.

Control flow: when cache/XRootD I/O completes, `Done()` first unreferences the associated `XrdPosixFile`, translates negative internal result values into `errno=-result` and callback result `-1`, then calls the user-implemented `Complete(ssize_t)`.

State and persistence: uses `theFile` pointer set by async issuers. It mutates only object reference counts and thread-local/process `errno`; no durable state.

Dependencies/integration: depends on `XrdPosixCallBack.hh` and `XrdPosixFile.hh`. Called through `XrdOucCacheIOCB` response scheduling in `XrdPosixFileRH` and extended pgread/pgwrite paths.

Risks: `Done()` assumes `theFile` is valid when invoked. Callback code runs after unref, so callers must not expect the file to remain alive unless they own another reference. `errno` is process/thread-local side effect before user callback.

Test signals: async success and failure callbacks; file close racing with async completion; callback observing correct result and `errno`.
