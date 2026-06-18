# sources/distributed-fs/xrootd/src/XrdOss/XrdOssTrace.hh

Purpose: defines OSS trace flags and lightweight macros used throughout XrdOss for conditional tracing and debug output.

Important APIs/types/functions: flags `TRACE_ALL`, `TRACE_Opendir`, `TRACE_Open`, `TRACE_AIO`, `TRACE_Debug`; macros `QTRACE`, `TRACE`, `TRACEReturn`, `DEBUG`, and `EPNAME`.

Control flow: in non-`NODEBUG` builds, trace macros check `OssTrace.What` against the selected flag and route messages through `SYSTRACE` with `tident` and `epname`. In `NODEBUG` builds, the macros compile to no-ops or direct returns.

State and persistence behavior: no owned state; behavior depends on the global `OssTrace` object configured elsewhere. Trace output is persisted only if the process logger writes it.

Dependencies: `XrdSysTrace.hh` and, for debug builds, `XrdSysHeaders.hh`. Call sites must define visible `OssTrace`, `tident`, and `epname` as expected by the macro expansion.

Integration points: used by OSS operations such as unlink, open, directory, and async I/O paths to make runtime diagnostics conditional without per-call virtual dispatch.

Risks: macro expansion depends on names in caller scope; `TRACEReturn` changes control flow; debug logging can expose paths and identifiers; `NODEBUG` changes observability significantly.

Test signals: compile with and without `NODEBUG`, enable each trace flag via config, verify messages include endpoint names, and ensure `TRACEReturn` returns expected error codes.
