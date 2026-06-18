# sources/distributed-fs/xrootd/src/XrdCl/XrdClTaskManager.cc

## Purpose

This file implements a single-threaded scheduled task runner. It runs short `Task` objects at requested times, supports self-rescheduling tasks, asynchronous unregister requests, and start/stop lifecycle around a pthread runner.

## Important APIs, Types, and Functions

`RunRunnerThread` is the pthread entry point. `Start` creates the runner and protects lifecycle with `pOpMutex`. `Stop` cancels and joins the runner. `RegisterTask` inserts a `TaskHelper` into the multiset. `UnregisterTask` queues a task pointer for later removal. `RunTasks` is the infinite scheduler loop.

## Control Flow

The runner disables cancellation while holding and processing task state. Each loop removes queued unregister requests, selects all tasks with `execTime <= now`, erases them from the active set, unlocks, and calls `Task::Run(now)` for each. A nonzero return value is treated as the next schedule time and reinserted; zero means complete and owned tasks are deleted. Cancellation is re-enabled only during the sleep interval.

## State and Persistence Behavior

State is in memory: resolution seconds, scheduled task multiset, unregister list, runner thread ID, running flag, and mutexes. Ownership is tracked per task. No task state is persisted by the manager.

## Dependencies and Integration Points

It depends on XrdSys mutex/timer/error text utilities, logging/default environment, constants, pthreads, and `Utils::TimeToString`. `Stream` uses it to schedule reconnect attempts through `StreamConnectorTask`.

## Risks and Edge Cases

The destructor deletes scheduled owned tasks but does not stop a running thread, so lifecycle users must call `Stop` before destruction. `Stop` uses pthread cancellation, so long-running `Task::Run` calls delay shutdown. `UnregisterTask` is asynchronous and does not interrupt a task already selected to run. `TaskHelperCmp` compares only execution time, so equal-time tasks rely on multiset equivalence handling and cannot be uniquely found by comparator alone.

## Test Signals

Tests should cover start/stop, one-shot deletion, rescheduling, unregister before execution, non-owned task retention, same-time task ordering/count, and delayed shutdown while a task is running.
