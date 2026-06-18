# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/condvar.c

This file implements kernel condition variables on top of hashed sleep queues, scheduler sleep-object callbacks, callout-backed timed waits, signal-aware waits, and listener wakeups.

Core behavior:
- `cv_sobj_ops` supplies owner, unsleep, and priority-change hooks for threads blocked on CVs; CVs have no owner.
- `cv_init()` initializes the compact waiter count; `cv_destroy()` asserts no waiters remain.
- `cv_block()` prepares the current thread for sleep, sets `t_wchan`, assigns `cv_sobj_ops`, accounts voluntary context switch/microstate sleep, increments `cv_waiters` up to `CV_MAX_WAITERS`, switches the thread to sleep state, and inserts it into the hashed sleep queue.
- `cv_wait()` blocks non-interruptibly, drops the associated mutex while asleep, switches, and reacquires the mutex.
- `cv_timedwait()`, `cv_reltimedwait()`, and `cv_timedwait_hires()` add callout-based wakeups and return remaining time or `-1` on timeout.
- `cv_wait_sig()` handles signal-interruptible waits for user LWPs, including scheduler-control cancellation, `lwp_asleep`, `lwp_sysabort`, `T_WAKEABLE`, and pending signal processing.
- `cv_timedwait_sig_hires()` combines timeout and signal behavior, with return precedence: signal/sysabort/cancel as `0`, timeout as `-1`, normal wake as positive remaining time.
- `cv_timedwait_sig()`, `cv_timedwait_sig_hrtime()`, and `cv_reltimedwait_sig()` are wrappers for tick-relative, hrtime-absolute, and tick-relative signal-aware waits.
- `cv_wait_sig_swap_core()` allows the sleeping thread to become swappable by clearing `TS_DONT_SWAP`; `cv_wait_sig_swap()` wraps it.
- `cv_signal()` wakes one waiter using the waiter hint if trustworthy, or consults the sleep queue when the hint has saturated.
- `cv_broadcast()` wakes all waiters and clears the waiter count.
- `cv_wait_stop()` periodically wakes to honor process stop/checkpoint/watchpoint/fork/lwp-suspend requests without general signal handling.
- `cv_waituntil_sig()` waits until an absolute wall-clock time and treats abrupt system time changes as a forced timeout so callers can reevaluate.

Important invariants:
- CV waits are invalid during quiesce and return immediately during panic.
- Callout wakeup is synchronized with actual blocking through `t_wait_mutex` to avoid wake-before-sleep races.
- `cv_waiters` is a bounded hint; when it reaches `CV_MAX_WAITERS`, signal paths must verify the sleep queue.
- Signal or timeout paths that observe they consumed a `cv_signal()` reissue `cv_signal(cvp)` so another waiter can receive it.
- `cv_signal()` and `cv_broadcast()` assert they are not running on interrupt stack.
- Associated mutexes are dropped only after the thread is fully queued for sleep.
