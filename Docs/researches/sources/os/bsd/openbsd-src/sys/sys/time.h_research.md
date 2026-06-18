# File Research: sources/os/bsd/openbsd-src/sys/sys/time.h

Defines `timeval`, `timespec`, `timezone`, interval timers, timeval/timespec arithmetic macros, and userland time-related prototypes. Kernel/standalone/libc paths add `struct bintime` and inline conversions among binary fractional time, nanoseconds, microseconds, `timespec`, and `timeval`.

Kernel/standalone declarations expose clock read APIs (`bintime`, `nanotime`, uptime/boottime/runtime variants), `clock_gettime`, interval timer maintenance, `settime`, rate checks, calendar conversion, BCD helpers, and saturated nanosecond conversion helpers. Filesystem code commonly depends on this through `timespec` in vnode attributes and inode timestamps.
