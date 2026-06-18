# sources/test-tools/stress-ng/stress-exit-group.c

Purpose: implements `exit-group`, verifying that the Linux `exit_group` syscall terminates all threads in a process by repeatedly forking a child that starts multiple pthreads and exits the group from thread context.

Important APIs/types/functions: `stress_exit_group_info_t` stores pthread handles and creation results. Static state includes `mutex`, `keep_running_flag`, shared `exit_group_failed`, `pthread_count`, and `pthreads[]`. `stress_exit_group_func()` calls `shim_exit_group(0)` from a pthread, `stress_exit_group_child()` starts and coordinates threads, and `stress_exit_group()` owns fork/reap and failure reporting.

Control flow: the parent maps a shared failure counter, sync-starts, and loops creating a mutex and forking a child. The child blocks SIGALRM, initializes thread state, starts up to 16 pthreads under a mutex, waits briefly for them to report started, and then calls `shim_exit_group(0)`. Each pthread sleeps until enough peers exist or stop is requested, then also calls `shim_exit_group(0)`. The parent waits for the child, destroys the mutex, and increments bogo operations.

State and persistence behavior: no durable state is stored. The only cross-process state is the anonymous shared `exit_group_failed` counter used to detect impossible returns from `exit_group`. Thread counts and flags are static process state inside each forked child.

Dependencies and integration points: requires pthread support and `__NR_exit_group`. Integrates with stress-ng mmap, pthread, signal, scheduler, process-state, and syscall shim helpers. Registered as `CLASS_SCHEDULER | CLASS_OS` with always-on verification.

Risks: pthread creation may hit `EAGAIN`, which shortens the child run. The static mutex is initialized in the parent and used after fork, so lifecycle ordering is important. A true `exit_group` failure would leave code paths that intentionally increment the shared failure counter.

Test signals: run `--exit-group` with short timeouts and process/thread limits, confirm no child or pthread leaks, no shared failure count, and unimplemented registration on non-Linux or non-pthread builds.
