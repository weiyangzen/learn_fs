# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_condvar.c

Read completely: 572 lines.

Implements NetBSD kernel condition variables on top of sleep queues. The private `kcondvar_t` storage holds a sleep queue and wait message. `cv_syncobj` integrates condition-variable sleeps with priority boosting, priority changes, lending, and unsleep handling.

`cv_init()` and `cv_destroy()` initialize and tear down the embedded sleep queue. `cv_enter()` hashes and locks the sleep queue, enqueues the current LWP, records whether the wait is interruptible, and releases the caller’s mutex. `cv_wait()`, `cv_wait_sig()`, `cv_timedwait()`, and `cv_timedwait_sig()` block through `sleepq_block()` and reacquire the mutex before returning. `cv_unsleep()` removes interrupted sleepers from the condition variable.

The bintime wait variants, `cv_timedwaitbt()` and `cv_timedwaitbt_sig()`, convert bintime timeouts into ticks, clamp very large waits, wait with at least one tick, and subtract elapsed tick time from the caller’s remaining-time value. `cv_signal()` and `cv_broadcast()` provide fast empty-queue checks and call noinline slow paths to wake one or all sleepers. Diagnostic helpers report waiters and basic validity.

Risks and notes: condition variables require the caller’s interlock discipline; `cv_signal()` and `cv_broadcast()` are documented for use with the interlocking mutex held or just released. Bintime waits are currently tick-based despite accepting an epsilon parameter, which is asserted but not otherwise used. The remaining-time update deliberately does not convert an explicit wakeup into `EWOULDBLOCK`, so callers must recheck their condition.
