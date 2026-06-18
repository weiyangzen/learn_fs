<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.cc

Purpose: Implements common log configuration, including logfile selection, logging plugin loading, plugin argv construction, and optional stderr forwarding into the logging subsystem.

APIs and control flow: `XrdOucLogging::configLog()` parses `configLogInfo::logArg`. `-` leaves stderr alone, plain paths configure a logfile, and `@library[,key=value...]` loads a `XrdSysLogPInit` plugin through `XrdOucPinLoader`. It parses plugin options such as `bsz`, `cse`, and `logfn`, calls `XrdSysLogging::Configure()`, exports `XRDLOGDIR`, and, when needed, redirects `STDERR_FILENO` through a pipe serviced by `LoggingStdErr()`. `configLPIArgs()` supplies plugin argv from `XrdOucEnv`, and `varVal()` extracts delimited key values.

State and persistence: Uses namespace statics `cseLvl` and `stdErr`; the stderr router thread is persistent once started. The configured logger and plugin are external subsystem state. `XRDLOGDIR` is exported process-wide.

Dependencies and integration: Integrates with `XrdSysLogging`, `XrdSysLogPI`, `XrdOucPinLoader`, `XrdOucEnv`, `XrdOucStream`, and `XrdOucUtils::subLogfn`.

Risks and test signals: Stderr redirection changes a process-global descriptor and must be tested with plugin/no-plugin combinations. `BadHdr()` filters captured lines for CSE modes, so tests should cover malformed headers, hi-res/keepV parameters, logfile substitution, plugin failures, and buffer size bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.cc -->
