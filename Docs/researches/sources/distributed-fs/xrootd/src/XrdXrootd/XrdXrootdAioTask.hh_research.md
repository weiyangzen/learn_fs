# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioTask.hh

Purpose: declares the abstract base class for xrootd asynchronous file-transfer tasks. It provides shared queueing, error, drain, and callback machinery while requiring derived classes to implement actual read/write copy loops.

Important APIs and types: public `Init()` binds a task to a protocol, response, and file. `Read()`, `Write()`, and `Recycle()` are pure virtual. Protected pure virtuals `CopyF2L()`, `CopyL2F()`, and `CopyL2F(XrdXrootdAioBuff*)` define data movement. Shared helpers include `Completed()`, `getBuff()`, `Drain()`, `SendError()`, `SendFSError()`, and `Validate()`. The class is both an `XrdJob` and a `gdCallBack`.

Control flow and state: the class owns pending-completion pointers, protocol/file/link references, offset and length counters, state flags (`aioDead`, `aioHeld`, `aioPage`, `aioRead`, `aioSchd`), in-flight count, done flag, and status enum. A union reuses linkage fields for normal AIO, page AIO, or FOB task queues; another union reuses `finalRead` and `pendWrite`.

Dependencies and integration: includes protocol and pthread/atomic helpers, forward-declares buffers and file objects, and is scheduled through `XrdScheduler`. `XrdXrootdAioFob` is a friend for queue linkage.

Risks and test signals: because unions reuse pointers by operation mode, derived classes must set `aioState` and lifecycle fields consistently. Tests should focus on derived-class interactions with `inFlight`, `Status`, callback failure, and recycle paths.
