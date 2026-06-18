# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_clock.c

## Purpose
Implements OpenBSD's high-level clock handling: initializing clock rates, maintaining hardclock ticks, converting time values to ticks, handling profiling/statistical clock samples, and exporting clock rate data via sysctl.

## Main Responsibilities
- Initializes `hardclock_period`, `statclock_avg`, `statclock_min`, `statclock_mask`, and `profclock_period` in `initclocks()`.
- Starts machine-specific clock setup via `cpu_initclocks()` and `cpu_startclock()`.
- Maintains global `ticks` and `jiffies` in `hardclock()`.
- Updates timeout machinery through `timeout_hardclock_update()`.
- Converts `timeval` and `timespec` durations to scheduler ticks with overflow-aware rounding in `tvtohz()` and `tstohz()`.
- Starts/stops profiling clocks per process using `startprofclock()` and `stopprofclock()`.
- Charges CPU time and resource usage in `statclock()`.
- Reports `struct clockinfo` through `sysctl_clockrate()`.

## Key Data
- `stathz`, `profhz`, `profprocs`: statistics/profiling clock rates and active profiling count.
- `ticks`: initialized near `INT_MAX` to exercise wraparound behavior.
- `jiffies`: volatile compatibility/global tick counter.
- `statclock_is_randomized`: controls whether statistical clock advances by random periods.

## Notable Control Flow
`statclock()` chooses user/kernel/interrupt/idle/spin accounting based on `clockframe` state, updates per-CPU `spc_cp_time` under `pc_lock`, updates per-thread `tusage`, and calls `schedclock()` every fourth statistical tick.

## Dependencies
Uses CPU clock hooks, timeout subsystem, scheduler accounting, UVM vmspace sizing, `clockintr` request helpers, and sysctl support.

## Research Notes
This file is the policy/accounting layer above `kern_clockintr.c`; it does not manage the per-CPU event queue itself.
