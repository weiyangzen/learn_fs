# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_clock.c

Read completely: 552 lines.

Implements machine-independent kernel clock handling for hardclock, statclock, schedclock, profiling clock control, clock tick sysctls, and entropy sampling from clock skew.

`initclocks()` calls MD clock initialization, adjusts `tick` and `tickadj` if `hz` changes, registers a fallback interrupt-resolution timecounter, computes profiling/stat ratios, creates `kern.clockrate` and `kern.hardclock_ticks` sysctls, and attaches hardclock/statclock random sources. `hardclock()` handles per-tick timers: entropy sampling, per-LWP process timers, fallback statclock, fallback scheduler clock at about 16 Hz, scheduler tick accounting, primary-CPU tick/timecounter advancement, heartbeat progress checks, and callout advancement.

`startprofclock()` and `stopprofclock()` maintain process profiling state and adjust `psdiv` when the statistics clock is the profiling source. `statclock()` samples entropy, updates per-CPU stat/prof divisors, records user/system/interrupt/idle CPU time, charges process tick counters, records profiling samples for user and optional kernel gprof/DTrace hooks, and runs cyclic DTrace clock hooks when enabled. `schedclock()` delegates runnable non-idle LWPs to scheduler accounting.

Risks and notes: if no separate statclock exists, profiling/statistics run from hardclock and comments explicitly say accuracy is poor. `hardclock_ticks` is advanced only by the primary CPU. `statclock()` changes the MD statclock rate when the per-CPU observed divisor changes. Interrupt time can be charged to the current process, by design, to account for real time spent in non-process work.
