# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/timers.c

Implements kernel time-of-day helpers, legacy interval timer syscalls, high-resolution time conversions, `nanosleep()`, and UTC/TOD conversion utilities.

Key responsibilities:
- Provides monotonically increasing timestamp generation via `uniqtime()` and 32-bit ABI conversion through `uniqtime32()`.
- Implements `gettimeofday()`, `getitimer()`, `setitimer()`, `xgetitimer()`, and `xsetitimer()` for native and 32-bit data models.
- Manages `ITIMER_REAL` through timeout callbacks, `ITIMER_VIRTUAL` and `ITIMER_PROF` in per-LWP timer state, and `ITIMER_REALPROF` through cyclic timers.
- Provides `itimerfix()`, `itimerspecfix()`, `itimerdecr()`, timeval/timespec add/sub/fix helpers, tick conversion helpers, and hrtime/timeval/timespec conversion helpers.
- Implements `nanosleep()` with signal-interruptible `cv_waituntil_sig()` and optional remaining-time copyout.
- Converts between Unix UTC seconds and `todinfo_t` calendar fields, caching the last UTC/TOD conversion under `tod_lock`.

Important paths:
- `uniqtime()` uses `gethrestime()`, protects cached last timestamp with `tod_lock`, and increments microseconds when needed to preserve uniqueness after small backward or equal time observations.
- `xsetitimer(ITIMER_REAL)` serializes concurrent callers with `SITBUSY`, cancels existing timeout IDs outside `p_lock`, stores an absolute fire time, and schedules `realitexpire()`.
- `realitexpire()` posts `SIGALRM`, clears one-shot timers, or advances periodic timers past current time before rescheduling.
- `xsetitimer(ITIMER_REALPROF)` removes any prior cyclic under `cpu_lock`, creates a low-level cyclic, cancels per-LWP `ITIMER_PROF`, and allocates per-thread `struct rprof` buffers opportunistically.
- `realprofexpire()` samples every LWP's microstate, increments real profiling state counters, marks ASTs, and pokes remote CPUs running target threads.
- `delete_itimer_realprof()` removes real profiling timers and pending/current `SIGPROF` state during exec.
- `timespectohz()` and `timespectohz64()` convert absolute or relative times to ticks with nonpositive and overflow protection.
- `hrt2ts()`, `ts2hrt()`, and `hrt2tv()` use optimized arithmetic on non-x86 paths and straightforward division/multiplication on modern x86 paths.

Locking and lifetime:
- `tod_lock` protects time-of-day conversion cache state and `uniqtime()`'s last timestamp.
- Process interval timer state is protected by `p_lock`; `xsetitimer()` deliberately drops it around `untimeout()` and cyclic operations.
- `cpu_lock` protects cyclic add/remove for `ITIMER_REALPROF`.
- `t_delay_lock` protects `nanosleep()` condition-variable waits.

Filesystem relevance:
- This is kernel timing infrastructure rather than filesystem code, but VFS, filesystem, block, and VM paths depend on these conversions, sleeps, timeouts, and timestamp helpers for I/O deadlines, attribute times, delay scheduling, and interruptible waits.
