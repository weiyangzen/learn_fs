# sources/distributed-fs/xrootd/src/XrdSys/XrdSysUtils.cc

Purpose: implements process/system utility helpers for executable path discovery, uname formatting, signal-name parsing, and signal blocking.

Important APIs/types/functions: `XrdSysUtils::ExecName()`, `FmtUname()`, `GetSigNum()`, and both `SigBlock()` overloads. The local `sigtab` maps selected signal names to numbers.

Control flow: `ExecName()` lazily computes and caches the executable path using `/proc/self/exe`, `_NSGetExecutablePath`, or Solaris `getexecname()`, returning an empty string on failure. `FmtUname()` formats platform-specific uname fields. `GetSigNum()` strips a leading `sig`/`SIG` and scans the table. `SigBlock()` ignores `SIGPIPE`, optionally installs a coverage SIGTERM dumper, builds a signal set, and calls `pthread_sigmask()`.

State and persistence: `ExecName()` stores a static heap string for process lifetime. Signal handlers and blocked masks affect the calling thread and, when called early, future threads.

Dependencies and integration: uses POSIX signals, pthread signal masks, uname, readlink, platform executable path APIs, and optional gcov support. It should be called early by daemon startup code.

Risks: `ExecName()` is only loosely thread-safe and may leak if raced. Blocking applies to the calling thread; callers must invoke it before thread creation for process-wide effect. Signal mapping is intentionally small and omits common signals such as `USR1`/`USR2`.

Test signals: executable path on Linux/macOS/Solaris, uname formatting per platform, signal lookup with and without `SIG` prefix, invalid signal names, and signal mask verification in child threads.
