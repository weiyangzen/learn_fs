# sources/test-tools/fs-mark/lib_timing.c

Purpose: small timing utility library for fs_mark/lmbench-style benchmarks using microsecond-resolution wall-clock time.

Important APIs/functions: `tvnow()` returns current epoch time in microseconds. `start(tv)` stores current time into caller-supplied `timeval` or a static default. `tvsub(tdiff, t1, t0)` subtracts timevals with underflow handling and clamps backwards time to zero. `tvdelta(start, stop)` returns microsecond delta. `stop(begin, end)` captures stop time if needed and returns elapsed microseconds.

Control flow/state: two static `timeval`s (`start_tv`, `stop_tv`) provide implicit timer storage when callers pass NULL. Most fs_mark calls use this implicit global timer around individual syscalls.

Dependencies/integration: includes POSIX time/filesystem headers and libc. Used by `fs_mark.c`.

Risks/test signals: static implicit timers are not thread-safe across real threads, but fs_mark uses forked processes so each child gets its own copy. Wall-clock `gettimeofday()` can move backwards; the code clamps to zero. Tests should verify null and explicit timer paths, negative adjustment behavior, and microsecond arithmetic.
