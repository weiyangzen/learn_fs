# sources/storage-engines/foundationdb/fdbclient/TaskBucket.cpp

## Purpose
`TaskBucket.cpp` implements a persistent, FoundationDB-backed task queue and future/callback mechanism. It lets tasks be enqueued, claimed, run by registered task functions, timeout-extended, requeued after timeout, finished, paused, and chained through `TaskFuture` callbacks.

## Important APIs, types, and functions
Registered task functions include `UnblockFutureTaskFunc`, `AddTaskFunc`, and `IdleTaskFunc`. `Task` stores reserved parameter keys and exposes `getDoneFuture()`, `getVersion()`, and `getPriority()`. `TaskBucketImpl` owns most actor logic: `getTaskKey()`, `getOne()`, `taskVerify()`, `finishTaskRun()`, `doTask()`, `dispatch()`, `watchPaused()`, `run()`, `isEmpty()`, `isBusy()`, `isFinished()`, `checkActive()`, `getTaskCount()`, `requeueTimedOutTasks()`, and `extendTimeout()`. Public `TaskBucket` wraps those helpers. `FutureBucket`, `TaskFuture`, and `TaskCompletionKey` implement persistent future state, joins, callbacks, and dependent task enqueueing.

## Control flow
Tasks are stored in an available subspace by priority unless they have a scheduled version, in which case they start in timeout space. `getOne()` optionally requeues timed-out tasks, searches priorities from high to low, randomly samples task IDs to reduce contention, moves the selected task's parameter keys from available space to timeout space, sets a timeout version, and updates an active marker. `doTask()` verifies optional validation keys, runs the registered task function while racing it with repeated timeout extension, then finishes inside a transaction. Dispatch keeps up to `maxConcurrentTasks` running, dynamically batches claims, and respects a pause key watched by `watchPaused()`. Future callbacks either run immediately if the future is set or are persisted under callback subspace until blocks are cleared.

## State and persistence behavior
All task state is persisted under the bucket prefix: available tasks under `av` or `avp`, active marker under `ac`, pause key, timeout records under `to`, and `task_count`. Future state is persisted under the future bucket prefix with block keys under `bl` and callback tasks under `cb`. Claiming, timeout extension, requeue, and finish are transactional transformations across these subspaces.

## Dependencies and integration points
It depends on `TaskBucket.h`, `FDBTypes`, `ReadYourWritesTransaction`, `Subspace`, tuples, Flow actors, `CLIENT_KNOBS`, transaction options, and registered `TaskFuncBase` factories. It is used by higher-level management workflows that need durable asynchronous task orchestration.

## Risks and edge cases
The queue relies on correct subspace layout and atomic task count updates. `requeueTimedOutTasks()` batches by key order and only safely moves complete tasks when range limits are respected; partial batches clear up to the last complete key. Long-running tasks must extend timeouts or they can be requeued and executed again. Validation keys abort stale tasks, but missing validation parameters make tasks invalid. `TaskFuture::performAllActions()` reconstructs callback tasks from key order, so callback subspace layout is critical. Recursive retry and dispatch loops can hide repeated transient errors unless trace counters are monitored.

## Test signals
No local `TEST_CASE`s are in this file, but useful tests include enqueue/claim/finish round trips, priority ordering, scheduled tasks, timeout requeue, timeout extension, pause/resume, task count watch, validation-key cancellation, future set/onSet/onSetAddTask behavior, joined futures, and duplicate execution resistance under injected transaction conflicts.
