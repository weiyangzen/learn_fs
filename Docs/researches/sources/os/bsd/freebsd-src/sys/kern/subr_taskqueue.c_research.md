# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_taskqueue.c

## Purpose
Implements FreeBSD taskqueues: priority-ordered deferred execution queues backed by software interrupts or kernel threads. Taskqueues are used broadly by drivers and kernel subsystems for asynchronous work.

## Core Structures
- `struct taskqueue` stores queued tasks, active/running tasks, sequence counters, callout count, lock, enqueue callback, context, name, worker threads, flags, and optional lifecycle callbacks.
- `struct taskqueue_busy` tracks a running task, active sequence number, and cancellation state.
- Queue flags include active, blocked, and unlocked-enqueue behavior.
- Timeout task flags track armed callouts and drains in progress.

## Queue Creation and Destruction
- `_taskqueue_create()` allocates queue/name storage, initializes lists and mutex, stores enqueue callback/context, detects queues that may drop the lock before enqueue callbacks, and marks the queue active.
- `taskqueue_create()` creates a normal mutex-backed taskqueue.
- `taskqueue_create_fast()` creates a spin-mutex-backed fast taskqueue.
- `taskqueue_free()` marks inactive, waits for workers/callouts to terminate, asserts no active tasks or armed timeout tasks remain, then frees resources.

## Enqueue and Scheduling
- `taskqueue_enqueue_locked()` inserts tasks by descending priority, counts repeated enqueues via `ta_pending`, supports `TASKQUEUE_FAIL_IF_PENDING` and `TASKQUEUE_FAIL_IF_CANCELING`, and calls the queue enqueue hook unless blocked.
- `taskqueue_enqueue_flags()` and `taskqueue_enqueue()` wrap locked enqueue.
- Timeout tasks use `_timeout_task_init()`, `taskqueue_enqueue_timeout_sbt()`, `taskqueue_enqueue_timeout()`, and `taskqueue_timeout_func()` around callouts.

## Execution
- `taskqueue_run_locked()` removes tasks from the pending queue, marks them active, drops the queue lock while running `ta_func`, reenters NET_EPOCH for network tasks, then wakes drain waiters.
- `taskqueue_run()` wraps execution with locking.
- `taskqueue_thread_loop()` runs worker-thread lifecycle callbacks, drains tasks until inactive, runs shutdown callbacks, decrements worker count, and exits.

## Draining, Cancellation, and Quiescence
- `taskqueue_cancel()` removes pending tasks and marks running tasks as canceling.
- `taskqueue_cancel_timeout()` stops the callout and cancels the queued task.
- `taskqueue_drain()` waits for a specific task to be neither pending nor active.
- `taskqueue_drain_all()` waits for tasks queued before the drain and tasks already active.
- `taskqueue_drain_timeout()` prevents timeout rearming, drains the callout, then drains the task.
- `taskqueue_quiesce()` loops until both queued and active work are empty.
- `taskqueue_block()`/`taskqueue_unblock()` suppress and resume enqueue-triggered execution.

## Built-In Queues
Defines:
- `taskqueue_swi`
- `taskqueue_swi_giant`
- `taskqueue_thread`
- `taskqueue_fast`

Software interrupt queues schedule SWIs; thread queues wake worker threads.

## Concurrency and Invariants
- Queue locking switches between normal mutex and spin mutex based on `tq_spin`.
- Running tasks are tracked in `tq_active`; drain and cancellation logic depends on this list.
- Some enqueue hooks are allowed after releasing the queue lock to avoid lock-order or spin-lock issues.
- `tq_callouts` also blocks queue teardown while timeout/drain operations are outstanding.

## Filesystem Relevance
Filesystem and storage drivers commonly use taskqueues for completion callbacks, deferred cleanup, timeout handling, and work that must not run directly in interrupt or lock-heavy contexts.
