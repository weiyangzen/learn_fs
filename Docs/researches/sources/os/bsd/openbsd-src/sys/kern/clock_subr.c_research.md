# File Research: sources/os/bsd/openbsd-src/sys/kern/clock_subr.c

Generic date/time conversion helpers.

Key behavior:
- `clock_ymdhms_to_secs()` converts `struct clock_ymdhms` to POSIX seconds since 1970.
- `clock_secs_to_ymdhms()` converts POSIX seconds back to calendar fields and weekday.
- Uses Gregorian leap-year logic with optimized common-case modulo avoidance.
- Handles February leap-day adjustment.

Filesystem/OS relevance:
- Kernel time conversion helper used by platform clock code and timekeeping paths.
