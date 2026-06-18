<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixTrace.hh

Purpose: Provides debug trace macros for the POSIX layer. It centralizes the debug bit, namespace declaration for `XrdPosixGlobals::Trace`, and no-op behavior under `NODEBUG`.

Important APIs/types/functions: `TRACE_Debug` defines the debug mask. In debug builds, `DMSG`, `DEBUGON`, `DEBUG`, and `EPNAME` wrap `XrdSysTrace` logging. In `NODEBUG`, `DEBUG` and `EPNAME` compile away and `DEBUGON` is false.

Control flow and state: Runtime state is the global `XrdSysTrace Trace` object defined in `XrdPosixXrootd.cc`; its mask is initialized from `XRDPOSIX_DEBUG`. Callers commonly create `EPNAME("Function")` and then guard debug-only string building with `DEBUGON`.

Dependencies/integration: Used by `XrdPosixPrepIO.cc`, `XrdPosixXrootd.cc`, `XrdPosixXrootdPath.cc`, and other POSIX files. PSS has a separate but similar tracing header.

Risks and test signals: Logging macros should not evaluate expensive or unsafe expressions when disabled. Tests are mostly build/runtime smoke signals: debug and `NODEBUG` builds must both compile, `XRDPOSIX_DEBUG` should enable expected trace output, and logs must obfuscate auth data where callers use `obfuscateAuth()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixTrace.hh -->
