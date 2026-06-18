# File Research: sources/os/bsd/dragonflybsd/sys/kern/usched_dummy.c

## Purpose

`usched_dummy.c` implements a simple example DragonFly user scheduler named `dummy`. It provides the same `struct usched` interface as the real schedulers but uses one global FIFO run queue, minimal priority logic, basic per-CPU current-user-LWP state, and helper threads. It is useful as a reference implementation for scheduler mechanics rather than as a sophisticated production scheduler.

## Main Responsibilities

- Registers `struct usched usched_dummy`.
- Maintains a single global `TAILQ` of runnable user LWPs.
- Tracks each CPU's current user LWP in `dummy_pcpu[]`.
- Uses `dummy_curprocmask` and `dummy_rdyprocmask` to publish CPUs with current user LWPs and CPUs ready to accept work.
- Handles acquire/release, runqueue insertion, selection, yield, priority reset, fork initialization, and helper-thread wakeup.
- Exposes `kern.usched_dummy_rrinterval`.

## Scheduling Model

The scheduler defines the same priority base ranges used by BSD4-style user schedulers, but it does not maintain per-priority queues. `lwp_priority` and `lwp_estcpu` reuse the `lwp_usdata.bsd4` fields. All runnable LWPs that cannot immediately become a CPU's `uschedcp` are inserted at the tail of `dummy_runq`.

`dummy_runqcount` tracks the global queue length. `dummy_spin` protects the queue and cross-CPU helper decisions. Each CPU has only `rrcount`, `helper_thread`, and `uschedcp`.

## Core Control Flow

`dummy_acquire_curproc()` is called before userland return. It handles pending reschedule requests through `dummy_select_curproc()`. If the CPU has no current LWP and the global runqueue is empty, the caller becomes `uschedcp`. Otherwise the caller runs any passive release hook, deschedules itself, enqueues itself with `dummy_setrunqueue()`, switches away, and loops until some CPU selects it as current. The loop can migrate the thread.

`dummy_release_curproc()` checks that the LWP is not on a runqueue and, if it is the CPU's current user LWP, calls `dummy_select_curproc()`.

`dummy_select_curproc()` clears the reschedule request, pops the first LWP from `dummy_runq`, clears `LWP_MP_ONRUNQ`, installs it as `uschedcp`, marks the CPU current, acquires the LWKT thread, and schedules it. If the runqueue is empty, it clears the CPU's current-user bit.

`dummy_setrunqueue()` immediately assigns the LWP to the local CPU if that CPU has no current user LWP. Otherwise it inserts the LWP at the global queue tail, marks `LWP_MP_ONRUNQ`, gives away LWKT ownership, and wakes another ready helper CPU if one is available.

## Priority and Timer Behavior

`dummy_schedulerclock()` only implements round-robin timing. If an LWP is running and the per-CPU `rrcount` reaches `usched_dummy_rrinterval`, it resets the counter and requests user reschedule.

`dummy_recalculate_estcpu()` is empty. `dummy_forking()` copies the parent's `estcpu` to the child. `dummy_resetpriority()` maps `lwp_rtprio.type` and `prio` into broad priority bases and updates `td_upri` for normal priority. It does not reposition queued LWPs by priority because the runqueue is FIFO.

`dummy_yield()` simply requests user reschedule. `dummy_changedcpu()`, `dummy_exiting()`, and `dummy_uload_update()` are no-ops.

## Helper Threads and Initialization

`dummyinit()` initializes the global queue and spinlock and enables CPU 0 for dummy scheduling. `dummy_sched_thread_cpu_init()` creates one helper thread per active CPU, enables that CPU in the ready mask, and clears current-mask bits for CPUs other than CPU 0.

`dummy_sched_thread()` uses LWKT deschedule interlocking. Each helper marks itself ready, then either forwards the wakeup to another ready CPU if it already has `uschedcp`, pulls the first LWP from the global queue if it is idle, or goes back to sleep.

## Concurrency and Risk Notes

This file intentionally avoids advanced priority and affinity behavior. The global FIFO queue is simple but can contend on `dummy_spin`, does not preserve priority ordering, and only does minimal CPU-affinity handling. It still exercises sensitive scheduler mechanics: LWKT descheduling, `LWP_MP_ONRUNQ`, helper wakeups, current/ready CPU masks, and acquire paths that can migrate the thread.
