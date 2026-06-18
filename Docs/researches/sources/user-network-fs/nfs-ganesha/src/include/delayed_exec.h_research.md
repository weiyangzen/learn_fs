# sources/user-network-fs/nfs-ganesha/src/include/delayed_exec.h

## Purpose
`delayed_exec.h` declares a small delayed task executor for scheduling callback work after a nanosecond delay. It is intentionally simpler than the thread fridge and is used for upcall retry/recall/revoke style operations.

## Important APIs, Types, And Functions
The public API is `delayed_start`, `delayed_shutdown`, and `delayed_submit(void (*)(void *), void *, nsecs_elapsed_t)`. Delays are expressed in the project `nsecs_elapsed_t` type from `gsh_types.h`.

## Control Flow
`delayed_start` initializes a mutex, condition variable, AVL tree of execution times, and one detached executor thread. `delayed_submit` computes a realtime due date, inserts a task into an AVL bucket keyed by that time, and wakes the executor if the new task is earliest. The executor waits indefinitely when empty, timed-waits until the next due time, pops due tasks, unlocks, runs callbacks, and repeats. `delayed_shutdown` blocks new submissions, waits for active submitters, signals the thread, waits up to 120 seconds, and cancels remaining threads if needed.

## State And Persistence
State is process-local: an AVL timer tree, task lists, executor thread list, mutex, condition variable, `deny_submission`, active submitter count, and running/stopping state. There is no disk persistence. Pending tasks are lost on process shutdown.

## Dependencies And Integration Points
The implementation depends on pthreads, RCU thread registration, project AVL/list/memory/log utilities, `common_utils.h`, and atomic helpers. Callers include `FSAL_UP/fsal_up_top.c` for layout recall, delegation recall, revoke checks, and async returns.

## Risks
Only one executor thread is started, so long-running callbacks delay all later tasks. Callbacks execute outside the executor mutex but still share one worker. `delayed_submit` allocates before taking the lock and returns `EAGAIN` after shutdown begins. Shutdown uses asynchronous cancellation if the detached thread does not exit cleanly, so callback code must tolerate abrupt process teardown. Time is based on `CLOCK_REALTIME` via `now`, so wall-clock jumps can affect scheduling.

## Test Signals
Tests should verify zero-delay execution, ordered delayed execution, multiple tasks with identical due times, earliest-task wakeup, submission during shutdown, long callback behavior, shutdown with no tasks, shutdown while tasks are pending, and caller integration for upcall retries.
