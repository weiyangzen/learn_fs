# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpTrace.hh

Purpose: Defines XrdHTTP tracing flags and convenience macros around `XrdSysTrace`.

Important APIs/types/functions: Flags include `TRACE_AUTH`, `TRACE_DEBUG`, `TRACE_MEM`, `TRACE_REQ`, `TRACE_REDIR`, `TRACE_RSP`, and `TRACE_ALL`. In debug builds it declares external `XrdHttpTrace` and defines `TRACE`, `TRACEI`, `TRACING`, and `EPNAME`; in `NODEBUG` builds these are no-ops.

Control flow: Call sites set a local `TraceID` and optionally `TRACELINK`, then macros emit through `SYSTRACE` only when the relevant `XrdHttpTrace.What` bit is enabled.

State and persistence: Trace state is centralized in the external `XrdHttpTrace` object. This header itself has no storage.

Dependencies and integration points: Integrates with `XrdSysHeaders` and `XrdSysTrace`; used throughout HTTP security, request, protocol, and plugin code for runtime diagnostics.

Risks: Macros depend on call-site names such as `TraceID` and `TRACELINK`, so misuse produces compile failures or wrong link context. Trace option changes must stay aligned with config parsing.

Test signals: Compile with and without `NODEBUG`, enable individual trace masks, and verify link-scoped and non-link-scoped messages appear as expected.
