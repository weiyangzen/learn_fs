# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_synch.c

## Purpose

Implements core sleep/wakeup synchronization, pause helpers, blockcount waiting, machine-independent context switch accounting, load average maintenance, scheduler AST handling, yielding, and CPU-query syscalls.

## Main Responsibilities

- Initializes sleep queues in `sleepinit()`.
- Implements general sleep primitive `_sleep()`.
- Implements spin-mutex sleep primitive `msleep_spin_sbt()`.
- Implements `pause_sbt()` for timed delay/sleep, using busy delay during cold boot, KDB, or stopped scheduler.
- Implements wakeup APIs:
  - `wakeup()`
  - `wakeup_one()`
  - `wakeup_any()`
- Implements blockcount wake/wait helpers:
  - `_blockcount_wakeup()`
  - `_blockcount_sleep()`
- Implements machine-independent context switching in `mi_switch()`.
- Implements `setrunnable()` for transitioning a thread to runnable state.
- Maintains load average in `loadav()` and initializes scheduler callouts in `synch_setup()`.
- Handles scheduler AST preemption/yield path in `ast_scheduler()`.
- Implements yield helpers and syscalls:
  - `should_yield()`
  - `maybe_yield()`
  - `kern_yield()`
  - `sys_yield()`
  - `sys_sched_getcpu()`

## Important Control Flow

- `_sleep()` validates locking and sleep state, locks the sleep queue, drops Giant and the interlock as appropriate, enqueues the thread, installs timeout if requested, waits interruptibly or uninterruptibly, then reacquires locks unless `PDROP` was requested.
- `msleep_spin_sbt()` is the spin-mutex variant: it drops a spin mutex before sleeping and reacquires it afterward.
- `pause_sbt()` converts zero timeout to one tick and avoids scheduler sleeps when scheduler operation is not available.
- `_blockcount_sleep()` atomically coordinates a counter with waiters, avoiding sleeps when the count is already zero and returning `EAGAIN` after ordinary wakeups.
- `mi_switch()` validates switch context, records voluntary/involuntary switch counts, updates runtime accounting, emits tracing/probes, calls scheduler-specific `sched_switch()`, and stashes a dead thread after switch.
- `ast_scheduler()` restores user priority and switches with `SWT_NEEDRESCHED`.

## State, Tunables, and Locking

- `hogticks` controls yield heuristics.
- `pause_wchan[MAXCPU]` provides per-CPU pause wait channels.
- `averunnable` stores 1, 5, and 15 minute load averages using fixed-point constants.
- Sleep paths interact with lock classes, WITNESS, sleep queues, Giant, KTRACE, and signal interruption (`PCATCH`).
- `mi_switch()` requires the current thread lock on entry and releases it through scheduler switch mechanics.

## Filesystem Relevance

This file is directly relevant to filesystem blocking behavior. VFS, buffer cache, storage, and filesystem code use `_sleep()`, `msleep`, pause, wakeup, and blockcount waiting to coordinate I/O completion, vnode state changes, mount activity, shutdown drains, and background workers. Signal interruption semantics here combine with `kern_sig.c` to produce `EINTR`/`ERESTART` behavior in filesystem syscalls.

## Cautions

- `_sleep()` requires a valid interlock unless explicitly using `PNOLOCK` or a timeout-only style path; incorrect locking can race wakeups.
- `PDROP` means the caller does not regain the interlock.
- Context switching from KDB is redirected to debugger reentry/panic handling.
- `mi_switch()` must not be called from arbitrary critical-section states.
