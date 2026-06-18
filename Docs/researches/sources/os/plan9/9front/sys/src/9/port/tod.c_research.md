# File Research: sources/os/plan9/9front/sys/src/9/port/tod.c

Time-of-day and fast tick conversion implementation.

Key responsibilities:
- Initializes the time-of-day state from `fastticks()` and registers periodic overflow correction.
- Maintains fixed-point multipliers/dividers for converting between fast ticks, nanoseconds, and microseconds.
- Allows the fast clock frequency to be updated through `todsetfreq()`.
- Sets absolute time or gradual clock adjustments through `todset()`.
- Computes epoch nanoseconds in `todget()` while clamping normal reads so time does not move backward.
- Optionally returns raw fast ticks and monotonic nanoseconds.
- Converts between time-of-day nanoseconds, fast ticks, microseconds, milliseconds, and seconds.
- Builds 64-bit fractional conversion constants in `mk64fract()`.

Dependencies:
- Uses architecture `fastticks`, `mul64fract`, kernel clock ticks, `addclock0link`, and interrupt locks.

Notable behavior:
- Assumes synchronized CPUs on multiprocessor systems; the file comments call this out as architecture-sensitive.
- `todfix()` periodically folds large fast-tick deltas into `tod.off` and `tod.last` to avoid conversion overflows.
- Monotonic time has separate `monooff`/`monolast` state.
