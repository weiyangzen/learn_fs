# File Research: sources/os/bsd/freebsd-src/sys/sys/_clock_id.h

Shared clock and timer constant definitions for `time.h` and `sys/time.h`.

Defines:
- POSIX-visible clocks such as `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_THREAD_CPUTIME_ID`, `CLOCK_PROCESS_CPUTIME_ID`.
- BSD-visible clocks such as `CLOCK_VIRTUAL`, `CLOCK_PROF`, uptime/realtime/monotonic precise/fast variants, `CLOCK_SECOND`, and `CLOCK_TAI`.
- Linux-compatible aliases: `CLOCK_BOOTTIME`, `CLOCK_REALTIME_COARSE`, `CLOCK_MONOTONIC_COARSE`.
- Timer flags `TIMER_RELTIME` and `TIMER_ABSTIME`.

Important note:
- Comments document intentional glibc compatibility around POSIX visibility levels, and a temporary visibility exception for `CLOCK_UPTIME_FAST`.

Research relevance:
- User/kernel ABI constant header for time APIs.
