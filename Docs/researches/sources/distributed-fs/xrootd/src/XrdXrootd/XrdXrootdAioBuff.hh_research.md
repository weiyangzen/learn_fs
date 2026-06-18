# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioBuff.hh

Purpose: declares the base async-I/O buffer class that adapts `XrdSfsAio` completions to xrootd protocol tasks. The type stores the associated task and buffer, while preserving a hook (`pgrwP`) for the page-read/write derived type.

Important APIs and types: `XrdXrootdAioBuff` inherits from `XrdSfsAio` and overrides `doneRead()`, `doneWrite()`, and `Recycle()`. `Alloc(XrdXrootdAioTask*)` is the factory. Public `next` is used by task pending queues and the static free list. `pgrwP` is a constant pointer set to null for base buffers or to the derived `XrdXrootdAioPgrw` instance for page I/O. Protected members `reqP` and `buffP` hold the owning task and the current pool buffer.

Control flow and state: constructors are simple placement-style initializers used by factories. The class deliberately exposes queue linkage rather than hiding it behind containers because these objects are hot-path completion nodes.

Dependencies and integration: includes only `XrdSfs/XrdSfsAio.hh` and forward-declares buffer, task, normal AIO, and page AIO classes. Implementations integrate with the global buffer manager and `XrdXrootdAioTask::Completed()`.

Risks and test signals: because `next` and `pgrwP` serve multiple queues and downcast-free access paths, misuse can cause stale links or wrong derived-object handling. Tests should cover reuse after recycle, derived-object allocation through base free-list storage, and completion callbacks for both read and write paths.
