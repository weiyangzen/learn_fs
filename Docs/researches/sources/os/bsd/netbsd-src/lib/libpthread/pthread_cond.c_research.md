# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_cond.c

This file implements condition variables and condition-variable attributes. Condition variables use a lock-free waiter stack in `ptc_waiters`, a remembered associated mutex in `ptc_mutex`, and optional private clock storage. It supports libc stub fallback through `__uselibcstub` and exports libc strong aliases.

`pthread_cond_timedwait` validates the condition and mutex, checks for pending cancellation, atomically pushes a stack-allocated waiter with the current LWP id, unlocks the mutex, parks with the selected clock and absolute timeout, then relocks the mutex. If cancellation or timeout/error races with a signal, it broadcasts to ensure any absorbed wakeup is not lost and waits until its waiter record is no longer globally visible. Cancellation exits only after the mutex has been reacquired, matching POSIX requirements.

`pthread_cond_signal` uses a dummy sentinel pointer to lock the waiter list, removes one waiter, and transfers it to the associated mutex through `pthread__mutex_deferwake`. `pthread_cond_broadcast` atomically steals the whole waiter list and similarly defers wakeups to mutex unlock. Attributes support `CLOCK_MONOTONIC` and `CLOCK_REALTIME`; process-shared support returns `ENOSYS` when enabled.

Risks are subtle memory-ordering requirements, stack waiter lifetime, and the single remembered mutex pointer when applications misuse a condition variable with multiple mutexes.
