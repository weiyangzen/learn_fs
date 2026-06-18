# sources/distributed-fs/xrootd/src/XrdSys/XrdSysTrace.hh

Purpose: declares the `XrdSysTrace` stream-style tracing class and simple formatting enum.

Important APIs/types/functions: `Xrd::Fmt` values `dec`, `hex`, `hex1`, `oct`, `oct1`; macro `SYSTRACE`; `Beg()`, `End()`, `SetLogger()`, `Tracing()`, public trace mask `What`, and insertion operators for common scalar types and strings.

Control flow: users call `trace.Beg(...) << pieces << trace.End()` or the macro. The object serializes message construction with `myMutex`, accumulates iovec fragments, and emits when the end sentinel is inserted.

State and persistence: each object keeps trace mask, logger, instance name, formatting state, buffers, and a mutex. It is reusable but not reentrant while a trace is in progress.

Dependencies and integration: includes `sys/uio.h`, `iostream`, `XrdSysPthread.hh`, and forward-declares `XrdSysLogger`. Components can plug into either logger objects or callback-based routing.

Risks: callers can forget to send `End()`, leaving the mutex locked. The macro assumes a variable-like object expression and debug operand formatting. Public `What` has no synchronization, so concurrent trace-mask updates need external ordering.

Test signals: compile all insertion overloads, macro use, runtime mask filtering with `Tracing()`, and callback routing.
