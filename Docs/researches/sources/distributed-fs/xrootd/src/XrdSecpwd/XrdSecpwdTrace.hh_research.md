# sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdTrace.hh

Purpose: small trace macro header for the password security module. It centralizes debug, authentication, and dump tracing behind `XrdOucTrace`.

Important APIs and types: exposes `QTRACE`, `PRINT`, `TRACE`, `NOTIFY`, `DEBUG`, and `EPNAME` macros when `NODEBUG` is not defined. Defines trace bit masks `TRACE_ALL`, `TRACE_Dump`, `TRACE_Authen`, and `TRACE_Debug`, and declares external `XrdOucTrace *pwdTrace`.

Control flow: callers declare an endpoint name with `EPNAME()` and call trace macros. `QTRACE` checks `pwdTrace->What` against the requested bit, `PRINT` wraps output in `Beg()`/`End()`, and `TRACE` conditionally prints. In `NODEBUG` builds, macros expand to empty forms.

State and persistence: no persistence. Runtime state is the external trace pointer and its `What` mask.

Dependencies and integration: includes `XrdOucTrace.hh` and, for debug builds, `XrdSysHeaders.hh` for stream output. Integrated by password protocol code that wants compile-time removable diagnostics.

Risks: macro-based logging can evaluate stream expressions only when active, but callers must still ensure referenced names such as `epname` exist. The file banner says `XrdSecgsiTrace.hh`, likely copy-paste drift. Empty `QTRACE(x)` in `NODEBUG` can be unsafe if used in expression contexts expecting a value.

Test signals: compile modules with and without `NODEBUG`, verify trace masks enable expected output, and check no password secrets are logged at normal debug levels.
