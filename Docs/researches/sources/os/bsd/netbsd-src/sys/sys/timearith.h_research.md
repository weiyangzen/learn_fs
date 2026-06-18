# File Research: sources/os/bsd/netbsd-src/sys/sys/timearith.h

Read completely: 77 lines.

Declares kernel time arithmetic validation and conversion helpers.

Key elements:
- Forward-declares `itimerspec`, `timespec`, and `timeval`.
- Declares `tstohz()` and `tvtohz()` for converting timespec/timeval durations to ticks.
- Declares `itimerfix()` and `itimespecfix()` for validating/fixing timer intervals.
- Declares `itimer_transition()` for computing interval timer transitions and overrun state.

Risks and notes:
- Conversion to ticks is boundary-sensitive for very small, huge, or invalid intervals.
- Used indirectly by kernel time APIs included from `sys/time.h`.
