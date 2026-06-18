# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogger.cc

Purpose: implements SSI logging globals and the `XrdSsiLogger` static API. It routes server messages to `XrdSysError`/`XrdSysLogger` and can intercept XRootD client log output through an `XrdCl::LogOut` adapter.

Important APIs and control flow: globals include `XrdSsi::Log`, `Logger`, `Trace`, `msgCB`, and `msgCBCl`. `Msg()`, `Msgf()`, and `Msgv()` write prefixed errors with `Log.Emsg()` or unprefixed lines with `Log.Say()`. The iovec overload writes directly with `Logger->Put()`. `SetMCB()` stores server callback and, for client/all modes, replaces the `XrdCl::DefaultEnv` log output with `LogMCB`. `LogMCB::Write()` strips leading XrdCl bracket fields, captures time/thread ID, and calls the configured callback. `TBeg()`/`TEnd()` wrap trace-stream output.

State and persistence: state is process-global logging configuration. No persistent storage is written here, but messages flow to the configured XRootD logger. Dependencies include XRootD logging, tracing, pthread thread numbering, and client default environment.

Integration points: used by SSI provider/service code and optionally by plugin callbacks installed at library initialization. Risks include `Logger` being null before initialized, ownership/leak expectations for `new LogMCB`, callback thread-safety, format truncation at 2048 bytes, and macro typos in the header using `XrdSSiLogger` capitalization. Test signals should cover callback installation, client log stripping, null client log behavior, and server `Msg*` output formatting.
