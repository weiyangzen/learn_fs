# File Research: sources/os/plan9/plan9/sys/src/9/port/portclock.c

Implements portable high-resolution timer queues and the periodic clock path.

Key responsibilities:
- Maintains one sorted timer list per Mach in `timers[MAXMACH]`.
- `timeradd` and `timerdel` add, modify, or remove relative/periodic timers with required lock ordering.
- `timerintr` dispatches expired timers, reschedules periodic timers, and defers `hzclock` calls for timers whose callback is nil.
- `timersinit` initializes time-of-day support and installs the periodic HZ timer.
- `addclock0link` adds periodic callbacks on CPU 0, synchronized to HZ when `ms == 0`.
- `hzclock` updates ticks, records PC, flushes MMU if requested, accounts time, invalidates kmaps, calls profiling/alarm hooks, and requests scheduling.
- `tk2ms` and `ms2tk` convert ticks and milliseconds with overflow avoidance.

Important behavior:
- Periodic timers of equal period can share phase by copying an existing timer’s `twhen`.
- `timerintr` caps loop iterations with `Maxtimerloops` diagnostics to catch timer/cycle-counter problems.
- `hzclock` exits other processors if `active.exiting` is set.

Dependencies:
- Platform must supply `fastticks`, `ns2fastticks`, `timerset`, `todinit`, and clock interrupt entry.
