# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsQueue.cc

## Purpose

This file implements a simple pthread-based work queue used by XrdFfs fan-out operations. It allows operations against many data servers to run concurrently without binding the code to C++ threading abstractions.

## Important APIs, Types, and Functions

Queue APIs are `XrdFfsQueue_create_task()`, `XrdFfsQueue_wait_task()`, `XrdFfsQueue_free_task()`, and `XrdFfsQueue_count_tasks()`. Worker APIs are `XrdFfsQueue_create_workers()`, `XrdFfsQueue_remove_workers()`, `XrdFfsQueue_count_workers()`, and the internal `XrdFfsQueue_worker()`.

Global state includes head/tail task pointers, monotonic task id, task mutex/condition, worker count/id, and worker mutex.

## Control Flow

`create_task()` allocates a task, initializes synchronization, and enqueues it. `dequeue()` blocks on the queue condition until a task exists. Worker threads repeatedly dequeue tasks, execute `task->func(task->args)` unless the task is a sentinel with `done == -1`, mark the task done, signal waiters, and either continue or exit.

`remove_workers()` enqueues one sentinel task per worker to remove and waits for each sentinel to be processed before freeing it.

## State and Persistence Behavior

All state is process-local. Tasks are heap-allocated by callers and must be freed after completion. Workers are detached pthreads with a configured 2 MiB stack.

## Dependencies and Integration Points

The queue is used by `XrdFfsPosix_*all()` fan-out operations and is started by `XrdFfsMisc_xrd_init()` or the FUSE executable init path. It can be compiled out with `NOUSE_QUEUE`.

## Risks and Edge Cases

`XrdFfsQueueWorker_mutex` is declared but not statically initialized in this file, so correctness depends on zero-initialization being accepted for `pthread_mutex_t` on the platform or external initialization. `wait_task()` uses `if` rather than a loop around `pthread_cond_wait()`, so spurious wakeups can return early. Queue length is approximated from task ids and can be off by one or wrong after wrap.

## Test Signals

Tests should cover task ordering, multiple workers, worker removal, sentinel behavior, spurious-wakeup robustness, queue length under empty/single/multiple states, and fan-out integration under high concurrency.
