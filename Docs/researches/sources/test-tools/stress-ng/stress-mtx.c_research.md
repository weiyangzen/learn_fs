# sources/test-tools/stress-ng/stress-mtx.c

Purpose: implements `mtx`, an ISO C11 mutex stressor using `threads.h` `mtx_t` operations from multiple pthread-created threads.

Important APIs/types/functions: global `mtx_t mtx` is the contended lock. `pthread_info_t` stores args, pthread handle, creation status, and lock timing/count data. `mtx_exercise()` repeatedly locks/unlocks the C mutex and records occasional timing. `stress_mtx()` configures `mtx-procs`, initializes/destroys the mutex, creates threads, joins them, and reports nanoseconds per lock.

Control flow: after option resolution and `mtx_init(mtx_plain)`, the stressor synchronizes, creates up to the requested number of pthreads, and waits while the global continue flag remains true. Each thread reseeds randomness, sleeps briefly, then loops locking the mutex, incrementing lock count and bogo operations, and unlocking it. Every thousandth lock uses the slower timed path. On stop, the parent joins all created threads, sums durations/counts, destroys the mutex, and emits metrics.

State and persistence: state is in-process only: one global mutex and per-thread info records. No filesystem or kernel IPC state persists beyond pthreads.

Dependencies and integration: requires pthread library, `threads.h`, `mtx_t`, `mtx_init`, and `mtx_destroy`; uses stress-ng pthread helpers, timing, bogo counters, settings, and process state.

Risks and test signals: platform C11 thread support varies, and returning early after no threads are created currently skips `mtx_destroy()`. Useful signals are successful thread creation, no `mtx_lock`/`mtx_unlock` failures, nanoseconds-per-mtx metrics, and unimplemented status on builds without C11 mutex support.
