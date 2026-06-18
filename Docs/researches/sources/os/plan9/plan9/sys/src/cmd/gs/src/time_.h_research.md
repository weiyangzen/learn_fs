# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/time_.h

Purpose: Ghostscript wrapper for time-related system headers.

Key contents:
- Includes `std.h` and `gconfig_.h`.
- Includes `<sys/time.h>` when available.
- For Plan 9, SCO, AIX, DYNIX/ptx, GCC/glibc, and Intel compiler cases, includes both `<sys/time.h>` and `<time.h>`.
- Defines fallback `timeval` and `timezone` structs when no `<sys/time.h>` is available.
- Defines `gettimeofday_no_timezone` for SVR4.0.
- Includes `<sys/times.h>` when configured and defines `use_times_for_usertime`; supplies default `CLK_TCK` if missing.

Dependencies: `std.h`, `gconfig_.h`, system time headers.

Integration notes: Plan 9 is explicitly called out as needing both time headers.

Risks: fallback struct definitions assume no system definitions are already present.
