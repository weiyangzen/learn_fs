# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time.h

## Purpose
Core illumos time header for timeval-based APIs, interval timers, high-resolution kernel time, tick/time conversions, and user-visible `gettimeofday`/`settimeofday` compatibility declarations.

## Main Interfaces
- Defines `time_t`, `suseconds_t`, `struct timeval`, `struct timezone`, `struct itimerval`, `struct itimerval32`, `todinfo_t`, and `hrtime_t`.
- Provides 32-bit conversion and overflow macros for `timeval` and `itimerval`.
- Defines timer utility macros: `timerisset`, `timercmp`, `timerclear`, `timeradd`, `timersub`, plus `TIMESPEC_TO_TIMEVAL` and `TIMEVAL_TO_TIMESPEC`.
- Defines interval timer IDs `ITIMER_REAL`, `ITIMER_VIRTUAL`, `ITIMER_PROF`, and `ITIMER_REALPROF`.
- Defines time constants and conversions between seconds, milliseconds, microseconds, nanoseconds, ticks, `timeval`, and `timestruc`.
- Kernel declarations include TOD/high-resolution clock routines such as `tod_get`, `tod_set`, `gethrtime`, `gethrestime`, `hrt2ts`, `ts2hrt`, `itimerfix`, and DTrace tick hooks.
- User declarations cover `adjtime`, `getitimer`, `setitimer`, `utimes`, `futimes`, `lutimes`, `gettimeofday`, `settimeofday`, `gethrtime`, and `gethrvtime`.

## Dependencies And Relationships
Includes `sys/types32.h`, `sys/types.h`, `sys/time_impl.h`, and kernel-only `sys/mutex.h`; user extensions pull in `time.h` and `sys/select.h`. It is the public bridge between POSIX/SVr4 time structures and kernel high-resolution time internals.

## Research Notes
The header is careful about standards exposure and 32-bit ABI conversion. Reviewers should treat the tick conversion macros as kernel-facing arithmetic helpers tied to globals like `hz`, `nsec_per_tick`, and `usec_per_tick`.
