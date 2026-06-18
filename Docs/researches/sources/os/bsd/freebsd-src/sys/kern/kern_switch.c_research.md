# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_switch.c

## Purpose

Provides machine-independent scheduler switch helpers, critical-section preemption exit handling, and generic run queue manipulation used by scheduler implementations.

## Main Responsibilities

- Exposes `kern.sched.preemption` to report whether kernel preemption is compiled in.
- Optionally exposes scheduler switch statistics under `kern.sched.stats`.
- Implements `choosethread()` and panic-aware `choosethread_panic()`.
- Implements KBI wrappers for `critical_enter()` and `critical_exit()`.
- Implements `critical_exit_preempt()`, which performs pending preemption once the current thread exits its final critical section.
- Implements generic run queue primitives:
  - `runq_init()`
  - `runq_add()`
  - `runq_add_idx()`
  - `runq_remove()`
  - `runq_findq()`
  - `runq_first_thread_range()`
  - `runq_not_empty()`
  - `runq_choose()`
  - `runq_choose_fuzz()`
  - `runq_is_queue_empty()`

## Important Control Flow

- `choosethread()` asks scheduler-specific `sched_choose()` for a runnable thread and marks it running. During panic, `choosethread_panic()` rejects ordinary non-system threads unless they are the panic thread.
- `critical_exit_preempt()` checks `td_critnest`, ignores KDB-active state, temporarily disables interrupt preemption while acquiring the thread lock, then calls `mi_switch()` with preemption switch flags.
- Run queue state is represented by per-priority queues plus compact status words. Queue operations maintain both the `TAILQ` and the status bit for fast scanning.
- `runq_findq()` scans status words over an inclusive queue-index range and calls a predicate on non-empty queues.
- `runq_choose_fuzz()` optionally prefers a thread that last ran on the current CPU among the first few entries of the best queue.

## State, Tunables, and Locking

- Run queue callers are responsible for scheduler locking; these helpers manipulate supplied `struct runq`.
- `td_rqindex` records the queue index used for removal.
- `RQ_NQS <= 256` is asserted so queue index storage remains valid.
- Tracing uses `KTR_RUNQ`, `KTR_PROC`, and optional scheduler statistics counters.

## Filesystem Relevance

This file is infrastructure for all kernel execution, including filesystem threads, syncer activity, vnode reclaim workers, and interruptible filesystem sleeps. It does not implement filesystem policy, but its run queue and preemption behavior affects latency and fairness of filesystem work.

## Cautions

- Run queue status bits must remain consistent with queue emptiness; assertions check for impossible non-empty bits with empty queues.
- Panic scheduling deliberately restricts runnable threads to reduce further damage.
- `critical_exit_preempt()` depends on precise critical nesting and thread-lock semantics.
