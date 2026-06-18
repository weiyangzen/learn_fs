# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTrace.hh

## Purpose

`XrdCmsTrace.hh` defines CMS tracing masks and macros that wrap `XrdSysTrace`/`XrdSysError` logging. It provides compile-time no-op behavior under `NODEBUG` and category-gated runtime tracing otherwise.

## Important APIs and Types

Trace masks include `TRACE_Debug`, `TRACE_Stage`, `TRACE_Defer`, `TRACE_Forward`, `TRACE_Redirect`, `TRACE_Files`, and `TRACE_Space`, plus `TRACE_ALL`. Macros include `QTRACE`, `DEBUG`, `DEBUGR`, `TRACE`, `TRACER`, `TRACEX`, and `EPNAME`. Namespace globals `XrdCms::Trace` and `XrdCms::Say` are declared for shared logging.

## Control Flow

Call sites declare `EPNAME()` and invoke category macros. If tracing is enabled for a category, macros route through `SYSTRACE`; the `R` variants include `Arg.Ident`, so they are intended for contexts where an `Arg` object is in scope.

## State and Persistence Behavior

Runtime state lives in the global `Trace.What` mask and global error object. No persistent state is managed here.

## Dependencies and Integration Points

It integrates with XrdSys logging and is included throughout CMS source files. Macro names are short and become part of local compilation context.

## Risks and Edge Cases

Macros assume local variables such as `epname` and sometimes `Arg` exist. The no-debug branch removes statements entirely, so trace expressions must not have side effects needed for correctness.

## Test Signals

Build tests should compile representative files with and without `NODEBUG`. Runtime checks can set `Trace.What` and assert that only selected categories emit logs.
