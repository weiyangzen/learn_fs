# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_clock.c

## Purpose
Implements core kernel clock handling: hardclock ticks, statclock accounting, profiling ticks, CPU time sysctls, interval timer AST delivery, optional deadlock detection, and software watchdog support.

## Key Elements
- Public clock handlers: `hardclock()`, `statclock()`, `profclock()`.
- Clock setup: `initclocks()`.
- Frequency globals: `stathz`, `profhz`, `profprocs`, `psratio`.
- Per-CPU tick tracking: `DPCPU_DEFINE_STATIC(long, pcputicks)`.
- Time conversion: `tvtohz()`.
- Profiling control: `startprofclock()`, `stopprofclock()`.
- Sysctls: `kern.cp_time`, `kern.cp_times`, `kern.clockrate`.

## Initialization
`initclocks()`:
- Initializes `time_lock`.
- Calls machine/eventtimer clock initialization through `cpu_initclocks()`.
- Computes `profhz`, `stathz`, and profiling ratio.
- Registers AST handlers for deferred profiling updates and interval timer signals.
- Attaches watchdog handling.

## Hardclock
`hardclock(int cnt, int usermode)`:
- Updates per-CPU and global ticks using atomic compare-and-set.
- Handles virtual and profiling interval timers via `hardclock_itimer()`.
- Invokes PMC hooks when configured.
- Calls `tc_ticktock()` for global timecounter advancement.
- Optionally runs device polling.
- Decrements and fires the software watchdog.
- Dispatches `clk_intr_event`.
- Performs CPU tick calibration on the first CPU.
- Enqueues epoch callback group tasks when pending.

## Statclock And Profiling
`statclock()`:
- Charges user, nice, system, interrupt, or idle CPU states.
- Updates per-thread tick counters.
- Updates resource usage integrals and max RSS.
- Records scheduler trace probes.
- Updates thread runtime and calls `sched_clock()`.

`profclock()` records user-mode profiling samples for processes with `P_PROFIL`.

`startprofclock()` and `stopprofclock()` maintain `profprocs` and start/stop the CPU profiling clock when transitioning between zero and nonzero profiled processes.

## Time Conversion
`tvtohz()` normalizes user-provided `timeval` values, handles microsecond underflow/overflow, clamps negative times to one tick, clamps huge values to `INT_MAX`, and returns one extra tick to avoid early expiry.

## Optional Deadlock Resolver
Under `DEADLKRES`, a kernel thread scans all processes and threads for excessive blocking on turnstiles or sleepqueues. It uses tunable thresholds and panics when possible deadlock conditions persist.

## Watchdog
`watchdog_config()` converts watchdog interval commands to tick counts. `watchdog_fire()` enters KDB when available and interactive, otherwise panics.

## Research Notes
This file accounts CPU time at interrupt frequency and links low-level timer interrupts to scheduler, timecounter, resource accounting, profiling, watchdog, and eventhandler subsystems.
