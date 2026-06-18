# sources/test-tools/stress-ng/stress-sleep.c

## Purpose

`stress-sleep.c` implements the `sleep` stressor, which creates many pthreads per worker and repeatedly exercises short sleep primitives. It stresses scheduler wakeups, interruptible sleeps, high-resolution timer behavior, CPU idle-state residency delays, and x86 WAITPKG `tpause` when available. Verification is always enabled because the stressor checks that requested sleep durations do not complete earlier than expected.

## Important APIs, Types, and Functions

- `stress_ctxt_t` carries per-thread state: the shared `stress_args_t`, requested thread count, pthread handle, and underrun counter.
- `stress_sleep_times_t` stores both `stress_time_now()` and `CLOCK_MONOTONIC` readings so timing checks can tolerate platform clock differences.
- `stress_sleep_time_now()` captures wall-clock and monotonic timestamps, falling back to `stress_time_now()` if `clock_gettime(CLOCK_MONOTONIC)` fails or is unavailable.
- `stress_time_delta()` returns the larger observed delta across the two time sources to avoid falsely reporting underruns during clock warps.
- `stress_pthread_func()` is the worker thread body. It performs C-state residency sleeps, `nanosleep()`, `shim_usleep()`, optional `pselect()`, `select()`, and optional x86 `stress_asm_x86_tpause()`.
- `stress_sleep()` is the stressor entry point. It parses `sleep-max`, creates the counter lock, installs the `SIGALRM` handler, starts up to `sleep_max` threads, waits until stop, joins threads, aggregates underruns, and destroys the lock.

## Control Flow

The stressor determines `sleep_max` from settings or maximize/minimize flags, creates a shared bogo-operation lock, installs a `SIGALRM` handler that flips `thread_terminate`, and synchronizes with the global stress-ng start barrier. It then attempts to create up to `sleep_max` pthreads. Each thread loops while both `stress_continue(args)` and `thread_terminate == false`.

Inside each pthread iteration, the code first walks the CPU idle-state list from `stress_cpuidle_cstate_list_head()` and sleeps for each residency target using `nanosleep()`. It then runs fixed nanosecond sleep sequences via `nanosleep()`, fixed microsecond sequences via `shim_usleep()`, optional nanosecond sleeps through `pselect()`, optional microsecond sleeps through `select()`, and optional x86 `tpause` loops when WAITPKG is present. After the sequence it increments the bogo counter with `stress_bogo_inc_lock()`. The parent sleeps in a 10 ms interruptible loop until termination, then cancels the alarm, sets `thread_terminate`, joins all created threads, and fails if any underruns were detected.

## State and Persistence Behavior

Persistent state is limited to process-local globals under pthread builds: `stress_sleep_counter_lock`, `thread_terminate`, and a signal set. The large `ctxts[MAX_SLEEP]` array is static inside `stress_sleep()` and reused across invocations in the same process. Each thread writes only its own `underruns` field, while the bogo counter is protected by the shared stress-ng lock. The stressor has no file persistence and no external state beyond CPU idle-state discovery.

## Dependencies and Integration Points

The file depends on pthread support, `sys/select.h`, stress-ng's timing, locking, signal, synchronization, CPU idle, and bogo accounting helpers. Optional integration points include `CLOCK_MONOTONIC`, `pselect()`, `select()`, x86 WAITPKG detection through `stress_cpu_x86_has_waitpkg()`, and assembly `tpause`. The exported `stress_sleep_info` registers the stressor with classes `CLASS_INTERRUPT | CLASS_SCHEDULER | CLASS_OS`, its option table, and `VERIFY_ALWAYS`. Without pthread support it exports `stress_unimplemented`.

## Risks and Edge Cases

The stressor can request up to 30,000 threads per worker, so resource exhaustion is expected and handled for `pthread_create()` returning `EAGAIN`. Early wakeup checks depend on timing precision; the dual-clock delta reduces false positives but cannot eliminate timing noise on virtualized or heavily loaded systems. The signal handler writes a volatile boolean only, which is appropriate, but `thread_terminate` is global and should be reset if this entry point were ever reused in-process after a terminated run. Failure paths before `stress_lock_destroy()` can leak the counter lock if signal handler setup fails after lock creation.

## Test Signals

Good test signals include a successful run with `--sleep 1 --sleep-max 1`, a higher-thread resource-limited run showing the informational "could not reach requested threads" path, and verification failure absence under `--verify`. Platform coverage should include builds with and without `pselect()`, with x86 WAITPKG when available, and without pthread support to validate the unimplemented registration.
