# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_taskqueue.c

## Summary
Implements DragonFly’s regular taskqueue subsystem: prioritized deferred tasks, timeout tasks, software-interrupt queues, and per-CPU thread-backed taskqueues.

## Main Responsibilities
- Creates, finds, frees, blocks, unblocks, and runs taskqueues.
- Enqueues tasks by priority, counts repeated enqueues through `ta_pending`, and supports optional cross-queue migration via `taskqueue_enqueue_optq()`.
- Supports timeout tasks backed by callouts.
- Cancels and drains normal, simple, and timeout tasks.
- Starts taskqueue worker threads and runs their loop.
- Defines `swi`, `swi_mp`, and per-CPU `taskqueue_thread[MAXCPU]` queues at SYSINIT.

## Important Behavior
Tasks are not individually locked; the file warns not to share one task across per-CPU queues. `taskqueue_run()` passes the pending count to the task function and wakes waiters after completion. Thread-backed enqueue temporarily drops the spinlock around `wakeup_one()`.

## Risks
Freeing a queue marks it inactive and drains/rendezvous with worker threads; new enqueues then fail with `EPIPE`. Timeout cancellation must coordinate both callout state and queued task state. Cross-queue migration relies on careful `ta_queue` fences and can leave pending work on the original queue.
