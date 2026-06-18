# File Research: sources/os/bsd/dragonflybsd/sys/sys/_clock_id.h

Read completely: 57 lines.

This small public header defines POSIX clock IDs and timer flags under feature-test visibility guards.

Key contents:
- POSIX clocks: `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_THREAD_CPUTIME_ID`, and `CLOCK_PROCESS_CPUTIME_ID`.
- BSD/FreeBSD-derived clocks: `CLOCK_VIRTUAL`, `CLOCK_PROF`, uptime/realtime/monotonic precise and fast variants, and `CLOCK_SECOND`.
- Timer flags: BSD `TIMER_RELTIME` and POSIX `TIMER_ABSTIME`.

Security/reliability notes:
- No runtime logic. The main compatibility issue is that constants are only exposed when the relevant `__POSIX_VISIBLE`/`__BSD_VISIBLE` guards allow them.
