# File Research: sources/os/bsd/netbsd-src/sys/sys/timevar.h

Read completely: 296 lines.

Defines kernel timekeeping and interval timer internals.

Key elements:
- Defines `struct itimer_ops`, common `struct itimer`, POSIX `struct ptimer`, timer table limits, and `struct ptimers`.
- Declares high-precision and cached time query APIs for uptime, realtime, and boottime in bintime/timespec/timeval forms.
- Declares clock syscall helpers, timer helpers, nanosleep, settimeofday, POSIX timer creation, timeout conversions, and rate checking.
- Declares interval timer lifecycle, locking, get/set, process timer tick, and process timer cleanup.
- Provides fast `time_second`, `time_uptime`, and `time_uptime32` accessors, using atomic load/store when available.
- Defines `DEFAULT_TIMEOUT_EPSILON` and helpers converting monotonic seconds to wall time and back.

Risks and notes:
- Timer state is shared and concurrency-sensitive; `itimer_lock` contracts matter.
- Time query APIs differ in precision and cost; callers must choose appropriately.
- Timer table indexes reserve `[0..3]` for `setitimer(2)`.
