# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_sleepqueue.c

## Purpose

`subr_sleepqueue.c` implements FreeBSD sleep queues: wait-channel keyed queues of threads blocked in sleep/wakeup and condition-variable style APIs. Sleep queues differ from turnstiles because wait channels have no owner, so they do not propagate priority. They support timeouts, interruptible sleeps, signal aborts, broadcast/signal wakeups, assertions against API misuse, optional profiling, DDB inspection, and stack reporting.

## Main Data Structures

A `struct sleepqueue` contains:

- `sq_blocked[NR_SLEEPQS]`: thread queues, with `NR_SLEEPQS == 2`.
- `sq_blockedcnt[]`: per-queue counts.
- `sq_hash`: link used in both hash-chain and free-list contexts.
- `sq_free`: free sleepqueue objects lent by other waiters.
- `sq_wchan`: associated wait channel.
- `sq_type`: sleepq consumer type.
- `sq_lock`: associated interlock under `INVARIANTS`.

A `struct sleepqueue_chain` contains a list of active queues and a spin mutex. There are 256 hash chains selected by `SC_HASH(wchan)`.

Threads carry their own sleepqueue. The first waiter on a wait channel lends its queue to the channel. Additional waiters lend their queues into the active queue’s free list.

## Initialization

`init_sleepqueues()` initializes all hash chains and creates the UMA zone. `thread0.td_sleepqueue` is allocated immediately. UMA init/dtor functions initialize blocked queues and assert emptiness on free in invariant builds.

`sleepq_alloc()` and `sleepq_free()` allocate/free per-thread queues from UMA.

## Enqueue Path

`sleepq_lock(wchan)` and `sleepq_release(wchan)` lock/unlock the hash-chain spin lock. `sleepq_lookup(wchan)` requires the chain lock and searches for an active queue.

`sleepq_add(wchan, lock, wmesg, flags, queue)` enqueues the current thread. It validates that sleeping is allowed, creates or joins the wait-channel queue, checks consumer type and associated lock consistency, inserts the thread at the tail of the selected blocked queue, clears the thread’s own sleepqueue pointer, records wait metadata, and marks interruptible sleeps with `TDF_SINTR`.

`sleepq_set_timeout_sbt()` arms the current thread’s sleep callout with precomputed sbintime state and the current CPU as target.

## Sleep And Wake Flow

`sleepq_switch(wchan, pri)` performs the actual context switch if the thread remains on the sleepqueue. It handles races where the thread was already woken, already timed out, or the real-time clock changed for absolute real-time sleeps. Otherwise it calls scheduler sleep hooks, switches the thread lock to the sleepqueue chain lock, marks the thread sleeping, and calls `mi_switch()`.

`sleepq_wait()`, `sleepq_wait_sig()`, `sleepq_timedwait()`, and `sleepq_timedwait_sig()` are the public blocking variants. Timed and signal variants clear and report timeout/signal state after resume.

`sleepq_resume_thread(sq, td, pri, srqflags)` removes one thread from the queue, optionally adjusts priority, and makes it runnable if it is actually sleeping. It also handles the race where a thread is in signal-check logic and not yet sleeping.

`sleepq_remove_thread()` performs queue removal, returns a sleepqueue object to the thread, stops callouts where safe, clears wait metadata and interrupt/timeout flags, and emits wakeup probes.

`sleepq_signal()` wakes one thread from a wait channel. Normal behavior chooses the highest-priority waiter, oldest on ties. `SLEEPQ_UNFAIR` selects a recent sleeper while trying to avoid threads still context-switching.

`sleepq_broadcast()` wakes all matching waiters on a queue via `sleepq_remove_matching()`. `sleepq_chains_remove_matching()` scans all chains and removes matching threads globally.

`sleepq_remove(td, wchan)` wakes a specific thread if it is sleeping on the specified channel. `sleepq_remove_nested()` removes a thread and returns with the thread lock held.

## Signals, Timeouts, And Races

`sleepq_check_ast_sc_locked()` checks pending wakeup, signal, and suspension AST state while coordinating process locks and the sleepqueue lock to avoid missed signals.

`sleepq_catch_signals()` either switches to sleep or removes the thread immediately if a signal/suspend condition is pending.

`sleepq_timeout()` is the callout handler. It verifies that the callout still corresponds to the active sleep, sets `TDF_TIMEOUT`, and either wakes the thread if it is asleep or leaves the flag for the thread to notice before switching.

`sleepq_abort(td, intrval)` aborts interruptible sleeps for signal delivery. If the thread has not fully slept yet, it records `td_intrval` and lets the sleeping path observe it; if already sleeping, it wakes the thread.

The real-time-clock generation check in `sleepq_switch()` handles the POSIX race between absolute real-clock sleeps and `clock_settime()`.

## Diagnostics And Profiling

With `STACK`, `sleepq_sbuf_print_stacks()` captures stacks for all threads sleeping on a wait channel/queue. It avoids allocation and sbuf writes while holding the sleepqueue spin lock by preallocating stack/sbuf storage and retrying with larger arrays.

With `SLEEPQUEUE_PROFILING`, the file tracks hash-chain depths and sleep-message frequency through debug sysctls.

DDB `show sleepq` / `show sleepqueue` prints wait channel, type, associated interlock, blocked threads, and expected counts.

## Maintenance Notes

This file is concurrency-critical. Correctness relies on the lock choreography among sleepqueue chain locks, thread locks, process locks, scheduler locks, and callout state. The “thread has not slept yet” versus “thread is already sleeping” distinction appears in timeout, signal, and wakeup paths and must be preserved.

Any new wake path must return the borrowed sleepqueue to the thread exactly once and maintain `sq_blockedcnt`, `td_sleepqueue`, `td_wchan`, `td_wmesg`, `TDF_SINTR`, and `TDF_TIMEOUT` consistently.
