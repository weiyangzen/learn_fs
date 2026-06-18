# sources/test-tools/stress-ng/stress-nanosleep.c

## Purpose
`stress-nanosleep.c` implements the `nanosleep` stressor. It creates one or more pthreads that repeatedly issue very short `nanosleep(2)` calls, using fixed nanosecond, microsecond, millisecond, random, or CPU C-state-derived sleep durations. The stressor exercises timer interrupt delivery, high-resolution timer handling, scheduler wakeups, and optional cpuidle residency paths.

## Important APIs, Types, and Functions
The stressor is exported through `stress_nanosleep_info`, with `CLASS_INTERRUPT | CLASS_SCHEDULER | CLASS_OS`, `VERIFY_ALWAYS`, help text, and options for `nanosleep-threads` and `nanosleep-method`. `stress_nanosleep_method_t` maps option names to bit masks. `stress_ctxt_t` is the per-thread context: it carries `stress_args_t`, the cpuidle C-state list, local operation count, max operation quota, pthread handle, selected method mask, and optional overrun/underrun metric accumulators.

`stress_nanosleep_ns()` wraps `nanosleep()` and, when `clock_gettime(CLOCK_MONOTONIC)` is available, measures actual elapsed time against the requested interval. `stress_nanosleep_pthread()` runs the sleep loop for one worker thread. `stress_nanosleep()` is the stressor entry point, reading settings, allocating contexts, starting threads, aggregating counters, joining threads, and publishing sleep overrun metrics.

## Control Flow
The main stressor chooses the thread count from settings or min/max flags, divides the global bogo-op limit across threads, resolves the method mask, and optionally falls back from C-state mode to random sleeps when no cpuidle states are available. It installs a `SIGALRM` handler that sets the file-local `thread_terminate` flag, allocates `stress_ctxt_t` entries, and spawns threads.

Each thread loops while `stress_continue(args)` is true, `thread_terminate` is false, and its local max-op quota is not exceeded. C-state mode iterates the cpuidle list and sleeps for roughly `1000 * (residency + 1)` ns. Random mode tries a descending range of random sleep lengths. The fixed modes issue 1 ns, 1000 ns, and 1000000 ns sleeps. The parent enters sync wait, transitions to run state, periodically resets and sums per-thread counters into the shared bogo counter, then deinitializes on timeout or stop.

## State and Persistence
State is process-local and transient. `thread_terminate` and a global `sigset_t` are static file state. Per-thread counters and timing accumulators live in the allocated context array and are freed before return. Metrics are persisted only into stress-ng shared stats through `stress_metrics_set()`. No files or durable system state are changed.

## Dependencies and Integration Points
The implementation depends on `pthread_create`, `pthread_join`, `nanosleep`, `SIGALRM`, `clock_gettime`, stress-ng settings, logging, synchronization, bogo counters, and cpuidle helpers from `core-cpuidle.h`. It compiles to `stress_unimplemented` when pthread or nanosleep support is missing. It integrates with the global stress-ng lifecycle through `stress_proc_state_set`, `stress_sync_start_wait`, `stress_continue`, `stress_bogo_set`, and `stress_bogo_add`.

## Risks
The stressor can request up to 1024 threads, so resource exhaustion and `EAGAIN` from pthread creation are expected operating modes. The static `thread_terminate` flag is not reset at the start of `stress_nanosleep()`, so reuse in unusual in-process repeated invocations depends on process lifetime and prior state. Counter aggregation reads unsynchronized per-thread counters, acceptable for stress metrics but approximate. The underrun metric calculation appears suspicious: after subtracting overhead, it computes `(underrun_nsec / underrun_count) - underrun_nsec`, which likely subtracts the accumulated adjusted value rather than overhead. Very small sleep intervals make timing metrics highly scheduler and hardware dependent.

## Test Signals
Useful signals are successful build on both pthread and unimplemented paths, a short run such as `--nanosleep 1 --timeout 1 --metrics`, method parsing for `all`, `cstate`, `random`, `ns`, `us`, and `ms`, and runs with `--nanosleep-threads 1` and a larger thread count. On C-state-capable Linux systems, verify fallback messaging when C-states are unavailable and metrics emission for sleep overrun. Failure tests should include low thread limits to exercise the `EAGAIN` limited-thread path.
