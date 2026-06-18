# sources/distributed-fs/xrootd/src/XrdSys/XrdSysTimer.hh

Purpose: declares a small stopwatch-style timer class plus static time/sleep utilities used throughout XRootD.

Important APIs/types/functions: `Delta_Time()`, `Midnight()`, `TimeLE()`, `Report()` overloads, `Reset()`, `Seconds()`, `Set()`, `Snooze()`, `s2hms()`, `TimeZone()`, and `Wait4Midnight()`.

Control flow: construct or `Reset()` to establish `StopWatch`; later `Report()` calls compute and accumulate elapsed time since that point. Static helpers cover sleeps, formatting, timezone, and midnight boundaries.

State and persistence: instance state is just two `timeval` values. There is no synchronization, so one timer object should not be shared mutably across threads without external locking.

Dependencies and integration: includes POSIX `sys/time.h` or Windows time/winsock compatibility headers. XrdThrottle uses `XrdSysTimer::Wait()` for recompute pacing.

Risks: API uses wall-clock `timeval` rather than monotonic time. `TimeLE()` compares only seconds and ignores microseconds. Return types use `unsigned long` for current epoch seconds, which is platform-width dependent.

Test signals: constructor reset, `Set()` with a known timestamp, all `Report()` overloads, and cross-platform compilation.
