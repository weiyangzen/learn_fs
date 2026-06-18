# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/time_.h

Generic substitute for Unix `sys/time.h`.

Key points:
- Includes `std.h` and build-generated `gconfig_.h`.
- Includes `<sys/time.h>` when `HAVE_SYS_TIME_H` is set.
- For Plan 9, SCO, AIX, Sequent DYNIX/ptx, GCC/glibc, and Intel compiler cases, also includes `<time.h>`.
- Without `sys/time.h`, includes `<time.h>` and defines fallback `struct timeval` and `struct timezone` where needed.
- Defines `gettimeofday_no_timezone` for SVR4.0.
- Includes `<sys/times.h>` when available and defines `use_times_for_usertime`.
- Supplies fallback `CLK_TCK = 100` when missing.

Dependencies and interactions:
- Used by platform timing code such as user-time and wall-clock helpers.
- Plan 9 is explicitly listed in the dual `sys/time.h` + `time.h` inclusion path.

Research relevance:
- Portability wrapper for time APIs across Unix-like, Plan 9, and legacy environments.
