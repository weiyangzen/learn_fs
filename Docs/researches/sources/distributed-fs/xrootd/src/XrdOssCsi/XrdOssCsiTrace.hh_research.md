# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTrace.hh

## Purpose
Defines trace flags and macros for the OSS CSI checksum module.

## Important APIs and control flow
`TRACE_ALL`, `TRACE_Warn`, `TRACE_Info`, and `TRACE_Debug` define bit masks consumed by a global `XrdOucTrace` instance. In non-`NODEBUG` builds, `QTRACE()` checks whether a trace class is active. `TRACE()` emits a message through `OssCsiTrace.Beg()`/`End()` using the local `epname` and `tident` symbols expected in calling code. `TRACEReturn()` logs and returns an error code. `DEBUG()` emits debug-only messages. `EPNAME()` declares a static function name used by trace output. In `NODEBUG` builds the macros collapse to no-ops or bare returns.

## State, dependencies, and integration
The header depends on `XrdOucTrace.hh` and, for debug builds, `XrdSysHeaders.hh`/`std::cerr`. It does not define the global trace object; CSI implementation files declare it as `extern XrdOucTrace OssCsiTrace`.

## Risks and test signals
The macros assume caller scope contains compatible `tident` where `TRACE()` is used; missing symbols produce compile errors. Since `TRACE()` wraps stream expressions, side effects inside disabled trace expressions are skipped. Build tests should compile CSI with and without `NODEBUG`, and runtime tests should verify trace masks gate warnings/info/debug as expected.
