# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleTrace.hh

Purpose: Defines compile-time trace flags and macros for the throttle subsystem.

Important APIs/types/functions: The header exports TRACE_NONE, TRACE_ALL, TRACE_BANDWIDTH, TRACE_IOPS, TRACE_IOLOAD, TRACE_DEBUG, TRACE_FILES, and TRACE_CONNS. When NODEBUG is not set it includes XrdSysHeaders and XrdOucTrace, defaults XRD_TRACE to m_trace->, and defines TRACE(act,x), TRACEI(act,x), and TRACING(x). TRACE uses TraceID; TRACEI also expects TRACELINK->ID.

Control flow: Call sites wrap expensive diagnostic formatting behind TRACE or TRACING checks. At expansion time, XRD_TRACE What is masked with the requested flag, then Beg(), stream output to std::cerr, and End() delimit the trace record.

State/persistence: No persistent state is owned here. The macros depend on an ambient trace pointer, TraceID, and optionally TRACELINK supplied by the including class or function scope.

Dependencies/integration: This is tightly coupled to XrdOucTrace and the style used by XrdThrottleManager implementation files. NODEBUG removes tracing calls entirely.

Risks: Macro context requirements are implicit and can break compilation if included outside expected manager/link scopes. TRACE_ALL covers only 0x0fff; future flags outside that mask would not be included. std::cerr formatting side effects are skipped in NODEBUG builds.

Test signals: Compile throttle code with and without NODEBUG; enable individual trace masks and verify bandwidth, IOPS, IO load, file, and connection diagnostics appear only when requested.
