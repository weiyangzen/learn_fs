# File Research: sources/os/bsd/dragonflybsd/sys/sys/timespec.h

Timespec compatibility and POSIX interval timer structure definitions.

Key contents:
- Includes `sys/_timespec.h`.
- Under BSD visibility, defines `TIMEVAL_TO_TIMESPEC` and `TIMESPEC_TO_TIMEVAL`.
- Defines `struct itimerspec` with:
  - `it_interval`
  - `it_value`

Role:
- Supplies POSIX.1b timer structure used by `timer_*()` APIs.
- Provides a lighter include path than full `sys/time.h`.

Research notes:
- The conversion macros duplicate the definitions in `time.h` under visibility control.
