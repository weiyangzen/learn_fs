# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcTrace.hh

Purpose: defines XrdOssArc trace masks and convenience macros for debug/save/all tracing. It centralizes trace access through the global `XrdOssArcGlobals::ArcTrace`.

Important APIs/macros: masks include `TRACE_All`, `TRACE_Debug`, `TRACE_Save`, and `TRACE_None`. `TraceInfo(x,y)` declares per-function `TraceEP` and `TraceID`. `TRACE(act,x)`, `TRACEI(act,x)`, `TRACING(x)`, and `DEBUG(x)` wrap `SYSTRACE` when the relevant bit is enabled. `XRDOSSARC_TRACE` can be overridden but defaults to `XrdOssArcGlobals::ArcTrace.` including the trailing member access dot.

Control/state behavior: no persistent state is declared here beyond the external trace object. Call sites must invoke `TraceInfo` before `DEBUG`/`TRACE` so `TraceEP` and `TraceID` are in scope.

Dependencies/integration: includes `XrdSysHeaders.hh` and `XrdSysTrace.hh`; used across staging, filesystem monitor, backup, and config code. Risks are macro hygiene, confusing `TRACE_All` mask excluding the low debug/save bits by value, and compile-time dependence on variable names. Tests are mostly build-time and runtime trace-level checks: verify macros compile in representative functions and that config trace settings emit or suppress expected diagnostics.
