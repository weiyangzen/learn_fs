# sources/test-tools/stress-ng/stress-hrtimers.c

## Purpose
`stress-hrtimers.c` stresses high-resolution POSIX timers by forking child processes that create `CLOCK_REALTIME` timers delivering `SIGRTMIN` at high frequency. It can optionally adjust nanosecond delay to maximize timer rate.

## Important APIs, Types, And Functions
The option `hrtimers-adjust` enables adaptive delay. `stress_hrtimers_set()` fills an `itimerspec` from global `ns_delay`. `stress_hrtimers_handler()` increments the shared bogo counter under a stress-ng lock and cancels the timer when stopping, timeout, or pending interrupt is detected. `stress_hrtimer_process()` installs the realtime signal handler, creates/arms/deletes the timer, and adjusts delay based on `timer_getoverrun()`. `stress_hrtimers()` manages up to `PROCS_MAX` child processes.

## Control Flow
The parent installs SIGCHLD handling, allocates shared child pid records, creates a lock, forks eight children, waits at the global barrier, releases child barriers, then sleeps until stop. Each child waits on its per-pid barrier, applies scheduler/OOM settings, creates a timer, arms it, and periodically adjusts timing until `stress_continue()` becomes false. Parent teardown kills/reaps children and records signal rate.

## State And Persistence
Shared state includes global `s_args`, `timerid`, `time_end`, `ns_delay`, and a stress-ng lock. Child pid records are mmap-backed. No persistent state is written.

## Dependencies And Integration Points
Feature gates require librt timer APIs. Integration uses stress-ng process synchronization, locking, scheduler helpers, OOM adjustment, parent-death alarms, child reaping, bogo counters, and metrics.

## Risks
Signal handlers call a limited set of helper/shim functions and must preserve errno. Timer rates are scheduler and privilege sensitive; SCHED_RR may fail silently through the helper. Global timer state is per process after fork but would not be thread-safe. Resource exhaustion from timers should skip.

## Test Signals
Signals include successful skip on missing timer support, children start and reap cleanly, `hrtimers-adjust` changes delay without runaway, no stuck timers after stop, and plausible `hrtimer signals per sec` metrics.
