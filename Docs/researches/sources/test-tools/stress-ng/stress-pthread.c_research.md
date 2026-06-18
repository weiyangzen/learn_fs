# sources/test-tools/stress-ng/stress-pthread.c research

Purpose: implements `pthread`, a scheduler/OS stressor that repeatedly creates large batches of pthreads and exercises thread-related Linux APIs from each thread.

Important APIs, types, and functions: `stress_pthread_info_t` records pthread handle, creation status, index, and timing. Globals include a condition variable, mutex, spinlock, running flags, a thread count, and the static `pthreads[MAX_PTHREAD]` table. Thread bodies call robust-list syscalls, `tgkill`/`tkill`, optional x86 thread-area syscalls, `setns`, signal wait APIs, and `stress_pthread_tid_address()` for `PR_GET_TID_ADDRESS` and `set_tid_address`.

Control flow: `stress_pthread()` blocks `SIGALRM` and polls it through `stress_signal_alrm_pending()`, initializes synchronization primitives, optionally configures a priority-inheritance mutex, then loops creating up to `pthread-max` threads while holding the mutex. Threads start, increment `pthread_count` under a spinlock, wait on the condition variable until the parent broadcasts shutdown, exercise post-wait syscalls, and exit. The parent waits for all started threads or timeout, optionally sends `pthread_sigqueue`, broadcasts, joins, records startup latency, and repeats.

State and persistence: state is process-global and reset per batch; no files persist. Signal masks and global flags are intentionally process-scoped.

Dependencies and integration: requires pthread support and optionally futex robust-list, prctl, modify_ldt/thread-area, setns, and pthread signal queue support. It registers with scheduler and OS classes and `VERIFY_ALWAYS`.

Risks: `MAX_PTHREAD` is large, so resource exhaustion is expected and EAGAIN is accounted as a limited batch rather than a hard failure. The shared `pargs` object is reused during creation; thread code must copy or dereference quickly enough under local conventions. Cleanup depends on broadcast plus joins after stop flags.

Test signals: nanoseconds to start a pthread, percentage of configured pthreads created, robust-list/syscall failure logs, and successful destruction of synchronization primitives indicate coverage.
