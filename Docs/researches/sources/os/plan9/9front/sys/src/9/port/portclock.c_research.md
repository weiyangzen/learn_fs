# File Research: sources/os/plan9/9front/sys/src/9/port/portclock.c

Portable timer queue and periodic clock handling.

Key responsibilities:
- Maintains one sorted timer list per `Mach`.
- Adds and deletes relative/periodic timers with `timeradd()` and `timerdel()`.
- Runs due timers in `timerintr()`, requeueing periodic timers.
- Implements the HZ clock path in `hzclock()`: ticks, MMU flush request, accounting, DTrace tick, kmap invalidation, profiling, alarms, user profiling, and scheduling.
- Initializes the per-CPU HZ timer in `timersinit()`.
- Adds periodic CPU0 callbacks through `addclock0link()`.
- Provides overflow-safer `tk2ms()` and approximate `ms2tk()`.

Important behavior:
- Periodic timers with equal frequency can be phase-aligned.
- `timerdel()` handles the rare case where a timer callback is active on another CPU.
- A timer with `tf == nil` represents the HZ clock.
- Timers require lock ordering: `Timer` before `Timers`.

Notable risks:
- Periodic timer minimum is asserted at 100 microseconds.
- Timer callbacks run from interrupt context and must respect that environment.
