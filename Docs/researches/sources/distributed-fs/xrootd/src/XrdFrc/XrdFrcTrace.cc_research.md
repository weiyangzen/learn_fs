<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.cc -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.cc

## Purpose
`XrdFrcTrace.cc` provides the single definition of the FRC/FRM logging and tracing globals declared in `XrdFrcTrace.hh`. It gives all FRM/FRC code a shared `Say` error channel and a shared `Trace` controller.

## Important APIs And Objects
The file defines `XrdFrc::Say` as `XrdSysError(0, "frm_")`, establishing the default log prefix used before subsystem-specific configuration adjusts it. It defines `XrdFrc::Trace` as an `XrdOucTrace` bound to `Say`, so debug/trace macros write through the same logger as normal errors.

## Control Flow, State, And Persistence
There are no functions and no persistence. The only state is process-global logging state. Runtime code modifies `Trace.What` to enable trace masks; `XrdFrmConfig::Configure()` sets `TRACE_ALL` on `-d` and exports `XRDDEBUG=1`.

## Dependencies And Integration Points
This file includes only `XrdFrcTrace.hh`. It must be linked exactly once into binaries using `XrdFrc::Say` or `XrdFrc::Trace`; otherwise consumers either fail to link or accidentally get duplicate definitions if another translation unit defines them.

## Risks And Test Signals
The primary risk is link composition: every executable using FRC trace macros needs this object or an equivalent definition. Tests are mostly build/link tests plus runtime checks that `-d` enables debug output and logger binding in `XrdFrmConfig` redirects both `Say` and `XrdLog` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcTrace.cc -->
