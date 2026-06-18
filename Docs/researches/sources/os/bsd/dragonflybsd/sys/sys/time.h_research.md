# File Research: sources/os/bsd/dragonflybsd/sys/sys/time.h

BSD time structures, arithmetic macros, interval timers, kernel clock APIs, and userland time prototypes.

Key contents:
- Includes canonical `_clock_id`, `_timespec`, `_timeval`, and select definitions.
- Defines conversion macros:
  - `TIMEVAL_TO_TIMESPEC`
  - `TIMESPEC_TO_TIMEVAL`
- Defines `struct timezone` and DST constants.
- Defines timespec/timeval clear, set, compare, add, and subtract macros.
- Defines interval timer IDs and `struct itimerval`.
- Defines `struct clockinfo`.
- Kernel-only declarations include:
  - time globals and NTP adjustment globals
  - uptime/current-time accessors
  - interval timer validation/decrement
  - rate checking
  - time setting/adjustment
  - timeval/timespec-to-hz conversions
  - nanosleep helpers
  - FAT timestamp conversion
  - TSC target/delay helpers
- Userland declarations include `adjtime`, `gettimeofday`, `settimeofday`, `utimes`, `futimes`, `futimesat`, `lutimes`, `getitimer`, and `setitimer`.

Important behavior:
- Kernel exposes both approximate/simple second counters and precise micro/nano accessors.
- Userland exposes BSD/XSI APIs according to visibility macros.
- `HAVE_FUTIMESAT` is defined with the userland `futimesat` prototype.

Research notes:
- This header is shared ABI plus kernel clock API surface.
- It intentionally duplicates some conversion macros also available in `timespec.h`.
