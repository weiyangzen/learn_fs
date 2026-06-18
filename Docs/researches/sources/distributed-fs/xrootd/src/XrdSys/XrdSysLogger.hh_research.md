## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogger.hh

Purpose: declares `XrdSysLogger`, the local logging and log-rotation facade.

Important APIs/types/functions: constructor/destructor; nested abstract `Task::Ring()` for midnight work; `AddMsg`, `AtMidnight`, `Bind`, `Capture`, `Flush`, `originalFD`, `ParseKeep`, `Put`, static `setForwarding`, `setHiRes`, `setKeep`, `setRotate`, `traceBeg`, `traceEnd`, `xlogFN`, and public `zHandler`. Private helpers cover fifo creation, timestamping, rotation lock, rebinding, and trimming.

Control flow: callers configure binding/rotation, then write messages through `Put()`. Trace users call `traceBeg()` and `traceEnd()` around direct stream output under the logger mutex.

State and persistence: owns current log fd binding state, path strings, rotation suffix, queued midnight messages/tasks, keep policy, fifo path, and handler thread id. It creates/removes filesystem artifacts during rotation.

Dependencies and integration: depends on pthread wrappers and platform `iovec` support. Used by `XrdSysError`, `XrdSysLogging`, and tracing code.

Risks: caller-supplied tasks must outlive the logger's queue. `traceBeg`/`traceEnd` must be paired or the mutex stays locked. `setForwarding` is static global state affecting all logger instances.

Test signals: API compile coverage, trace lock pairing, keep option parsing, static forwarding behavior, destructor cleanup, and multi-logger capture/forwarding interaction.
