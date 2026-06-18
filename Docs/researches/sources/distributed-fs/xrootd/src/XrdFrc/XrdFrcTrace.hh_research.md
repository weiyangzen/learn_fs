<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.hh

## Purpose
`XrdFrcTrace.hh` centralizes trace masks and logging macros for the File Residency Manager code. It abstracts debug emission behind `NODEBUG` and binds all diagnostics to the global `XrdFrc::Say` and `XrdFrc::Trace` objects.

## Important APIs, Macros, And Types
The header declares `TRACE_ALL` and `TRACE_Debug`; `QTRACE`, `DEBUG`, `DEBUGR`, `TRACE`, `TRACER`, `TRACEX`, and `EPNAME` are active when `NODEBUG` is not defined. `DEBUGR` and `TRACER` include `Req.User`, so they are meant for request-processing contexts where a `Req` object exists. `VMSG` and `VSAY` depend on a visible `Config` object with `Verbose`, which couples the macros to FRM modules using the global config.

## Control Flow And State
Trace macros gate output on `Trace.What` bitmasks. `TRACEX` writes to `std::cerr` between `Trace.Beg()` and `Trace.End()`. When compiled with `NODEBUG`, debug/trace macros reduce to no-ops, removing both output and expression evaluation for their arguments.

## Dependencies And Integration Points
The header includes `XrdSysError.hh`, `XrdOucTrace.hh`, and, in debug builds, `XrdSysHeaders.hh` for stream support. It is widely used by XrdFrc and XrdFrm code for common diagnostics. The external globals are defined in `XrdFrcTrace.cc`.

## Risks And Test Signals
Macro coupling is the main risk: `VMSG` and `VSAY` require `Config`, while request-aware macros require `Req` and `epname` in scope. Incorrect use can become a compile-time failure or produce misleading prefixes. Tests should include debug and `NODEBUG` builds, verify `-d` trace activation, and exercise verbose-only messages in FRM config/admin commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.hh -->
