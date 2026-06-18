# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcTrace.hh

## Purpose
Defines trace levels and trace macros for the proxy file cache. It centralizes log-level labels, error-string formatting, IO path obfuscation, and compile-out behavior when `NODEBUG` is defined.

## Important APIs, Types, and Functions
- Trace numeric levels `TRACE_None` through `TRACE_DumpXL` and string constants.
- `trace_what_strings[]` external declaration for dynamic integer trace levels.
- `ERRNO_AND_ERRSTR(err_code)` helper.
- `TRACE`, `TRACE_INT`, `TRACE_TEST`, `TRACE_PC`, `TRACEIO`, `TRACEF`, and `TRACEF_INT` macros.

## Control Flow
Macros check `XRD_TRACE What` against the requested level and call `SYSTRACE` with `m_traceID`. IO/file variants append obfuscated remote paths or local cache paths. `TRACE_PC` executes caller-supplied pre-code only when the trace level is enabled.

## State and Persistence Behavior
No persistent state. Runtime behavior depends on the current `XrdSysTrace` object returned by `GetTrace()` or a custom `XRD_TRACE` definition.

## Dependencies and Integration Points
Depends on `XrdSysTrace`, `XrdSysE2T`, and XrdOuc obfuscation helpers. Every traced class must expose `m_traceID` and `GetTrace()` compatible with these macros.

## Risks and Test Signals
Risks include macro side effects, `TRACE_INT` indexing invalid levels, compile errors in `NODEBUG` because not every macro has a stub (`TRACE_INT`/`TRACE_TEST` are not stubbed here), and reliance on local `m_traceID`. Tests are mostly compile-configuration tests with/without `NODEBUG` and runtime log-level filtering checks.
