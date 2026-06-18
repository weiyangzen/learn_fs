# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_clock.c

## Summary
Implements DragonFly BSD core clock, timekeeping, CPU accounting, scheduler/stat clocks, NTP adjustments, PPS support, and timestamp APIs.

## Main Responsibilities
- Initializes per-CPU hardclock, statclock, and scheduler clock systimers.
- Maintains global ticks, scheduler ticks, uptime, realtime, boottime, basetime FIFO, and ticktime snapshots.
- Applies `adjtime`, NTP permanent/one-shot corrections, and leap-second adjustments.
- Charges CPU time to user, nice, system, interrupt, and idle buckets.
- Updates process timers, profiling, resource usage integrals, and scheduler accounting.
- Registers CPU percentage collection callbacks with `kcollect`.
- Exposes clock and CPU accounting sysctls.
- Provides micro/nano uptime and realtime APIs.
- Implements PPS ioctls/events and simple TSC delay helpers.

## Important Behavior
CPU 0 owns system-wide ticks, NTP correction, basetime updates, ticktime snapshots, `kpmap` timestamp updates, and leap-second state. Other CPUs copy hardtime state from CPU 0 through a FIFO/index scheme with memory fences.

`hardclock` also drives soft ticks, existential-lock pseudo ticks, VM/VFS cache rollups, process interval timers, and deferred work. `statclock` measures elapsed microseconds from the CPU timer and charges the interrupted thread/process. `schedclock` calls the user scheduler and updates resource usage maximum RSS.

Fast `getmicrotime`/`getnanotime` return ticktime snapshots; precise `microtime`/`nanotime` read the CPU timer and add current basetime.

## Filesystem/VFS Signals
Although not a filesystem file, it calls `vfscache_rollup_cpu()` from hardclock and supplies time APIs used by VFS timestamps, accounting, checkpointing, and timeout logic.

## Risks
The file relies on careful CPU-local state, memory fences, and CPU0-only basetime publication. Time can step for realtime corrections; comments warn `time_second` can backstep while uptime remains monotonic.
