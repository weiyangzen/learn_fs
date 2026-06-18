# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_clocksource.c

## Purpose
Provides common eventtimer management for kernel clocks. It selects and programs hardware event timers, supports periodic and one-shot modes, handles per-CPU timer state, broadcasts timer events on SMP, and integrates callout scheduling.

## Key Elements
- Active eventtimer: `timer`.
- Per-CPU state: `struct pcpu_state`, stored in `DPCPU_DEFINE_STATIC(timerstate)`.
- Public clocksource hooks: `hardclockintr()`, `cpu_initclocks_bsp()`, `cpu_initclocks_ap()`, `suspendclock()`, `resumeclock()`, `cpu_startprofclock()`, `cpu_stopprofclock()`, `cpu_idleclock()`, `cpu_activeclock()`, `cpu_et_frequency()`, `cpu_new_callout()`.
- Sysctls: `kern.eventtimer.timer`, `kern.eventtimer.periodic`, `kern.eventtimer.singlemul`, `kern.eventtimer.idletick`.

## Event Handling
`timercb()` is the hardware eventtimer callback:
- Ignores callbacks during reconfiguration.
- Records current `sbinuptime()`.
- Updates next periodic or one-shot tick time.
- For non-per-CPU timers on SMP, marks other CPUs needing hardclock IPIs when their events are due.
- Calls `handleevents()` on the current CPU.
- Sends `IPI_HARDCLOCK` to other CPUs as needed.

`handleevents()`:
- Runs overdue hardclock events.
- Runs overdue statclock events.
- Runs overdue profclock events when profiling is active.
- Processes callouts when `nextcall` or `nextcallopt` is reached.
- Computes the next CPU event and reprograms the timer if needed.

## Timer Programming
`loadtimer()`:
- Starts periodic timers aligned to their period.
- For one-shot timers, computes the earliest next event across CPUs when required and calls `et_start()` only when the programmed time changes.

`setuptimer()`:
- Adapts desired periodic/one-shot mode to active timer capabilities.
- Clamps `singlemul`.
- Computes a feasible timer period with `round_freq()`.

`configtimer()`:
- Stops or starts the active timer.
- Initializes all per-CPU next-event fields.
- Uses IPIs and per-CPU `action` flags to start/stop per-CPU timers on other CPUs.
- Uses `busy` to block callbacks during reconfiguration.

## Initialization
`cpu_initclocks_bsp()`:
- Initializes global and per-CPU timer locks/state.
- Selects requested timer or best available periodic/one-shot timer.
- Applies C3-stop handling.
- Chooses `hz`, `stathz`, `profhz`, `tick`, `tick_sbt`, and related periods based on timer capabilities.
- Starts the configured timer.

`cpu_initclocks_ap()` initializes AP-local timer state and performs a fake event handling pass to program per-CPU timers.

## Idle, Profiling, And Callouts
`cpu_idleclock()` may suppress unnecessary ticks while idle, unless disabled or unsafe for the active mode. `cpu_activeclock()` catches up skipped events when the CPU becomes active.

`cpu_startprofclock()` and `cpu_stopprofclock()` switch timer configuration or profiling state as needed.

`cpu_new_callout()` updates per-CPU next callout deadlines, reprograms one-shot timers locally, or sends an IPI to make the target CPU reprogram its timer.

## Research Notes
This file is the bridge between abstract eventtimer hardware and higher-level clock consumers in `kern_clock.c`. Race control depends on `busy`, per-CPU spin locks, and IPI-synchronized reconfiguration.
