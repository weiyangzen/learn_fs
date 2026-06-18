<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdGlobals.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdGlobals.cc

Purpose: defines global singleton-style objects required by the Xrd package.

Important APIs/types/functions: namespace `XrdGlobal` defines `Logger`, `Log`, `XrdTrace`, `Sched`, `BuffPool`, `tlsCtx`, `XrdNetTCP`, external `xlBuff`, and `devNull`.

Control flow: no functions; initialization happens during static object construction before daemon startup. `Log` and `XrdTrace` are wired to `Logger`, and `Sched` receives `Log`/`XrdTrace`.

State and persistence behavior: process-global runtime state. These objects persist for daemon lifetime and are intentionally not torn down. `tlsCtx` and `XrdNetTCP` start null and are set by configuration; `devNull` starts `-1` and is opened during configuration.

Dependencies: includes buffer, large-buffer, inet, scheduler, trace, logger, and error headers. Forward declares `XrdTlsContext`.

Integration points: most Xrd runtime modules reference these globals for logging, tracing, scheduling, buffer allocation, default TCP network, TLS context, and `/dev/null` fd. `XrdConfig.cc` is the main initializer of the mutable pointers/fd.

Risks: static initialization order across translation units can be fragile if other globals depend on these before construction. Global mutable state complicates tests and multi-instance embedding. `extern XrdBuffXL xlBuff` is defined elsewhere, so link order/source inclusion matters.

Test signals: link tests for globals; startup smoke tests verifying `Log`, `Sched`, `BuffPool`, and `XrdNetTCP` are initialized before protocol loading; tests should isolate global state between daemon instances where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdGlobals.cc -->
