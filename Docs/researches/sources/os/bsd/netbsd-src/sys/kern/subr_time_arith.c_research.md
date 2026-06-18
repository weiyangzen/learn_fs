# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_time_arith.c

Read completely: 582 lines.

This file centralizes overflow-aware time arithmetic and timeout normalization. It is written for both kernel use and `_TIME_TESTING` userland builds.

Key functions:
- `tvtohz` converts a validated `timeval` duration to ticks, rounding up and adding one tick for the current tick, with overflow clamps to `INT_MAX`.
- `tstohz` converts `timespec` to `timeval` with nanosecond-to-microsecond rounding, then delegates to `tvtohz`.
- `itimerfix` and `itimespecfix` validate interval timer values, reject invalid nanosecond/microsecond fields and negative seconds, and round sub-tick nonzero intervals up to one tick.
- `timespecaddok` and `timespecsubok` prove whether addition/subtraction can be done safely with the existing `timespecadd`/`timespecsub` macros, accounting for carry/borrow and signed `time_t` bounds.
- `itimer_transition` computes the next periodic timer expiry and overrun count, using a fast non-overflow path, then a nanosecond arithmetic path when values fit in signed 64-bit nanoseconds.

Integration: `subr_time.c`, interval timers, sleeps, and timer syscalls depend on these helpers to avoid ad hoc overflow behavior.

Reliability notes: the overflow-checking functions rely on valid normalized timespec inputs and enforce that with `KASSERT`. `itimer_transition` falls back to clearing `next` on overflow or values too large to convert to nanoseconds, limiting representable periodic calculations to the signed 64-bit nanosecond range on that path.
