# sources/test-tools/fio/os/windows/posix/include/sys/resource.h

Purpose: exposes the small `getrusage()` surface fio needs on Windows.

Important APIs/types: defines `RUSAGE_SELF` and `RUSAGE_THREAD`; declares `struct rusage` with user/system time and a few counters; declares `getrusage()`.

Control flow and state: `posix.c` fills `ru_utime` and `ru_stime` using `GetProcessTimes()` or `GetThreadTimes()` and zeroes the structure first.

Dependencies and integration: supports fio CPU accounting paths that use `getrusage()` cross-platform.

Risks: only CPU time is meaningfully filled; context-switch and fault counters remain zero. Time conversion truncates to whole seconds.

Test signals: compare monotonic nondecreasing user/system times for process and thread usage on Windows.
