<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TaskBucket.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TaskBucket.h

## Purpose
`TaskBucket.h` declares a database-backed asynchronous task framework. A `TaskBucket` stores tasks in subspaces, executors reserve and run them with at-least-once semantics, and `FutureBucket`/`TaskFuture` provide database-backed completion and callback chaining.

## Important APIs, Types, and Functions
Important types include `Task`, `TaskParam<T>`, `ReservedTaskParams`, `TaskBucket`, `FutureBucket`, `TaskFuture`, `TaskFuncBase`, registration macros, and `TaskCompletionKey`. Main methods cover adding tasks, reserving `getOne`, executing `doTask`/`doOne`/`run`, pausing, clearing, finishing, extending timeouts, keep-running validation, checking emptiness, task counts, futures, future joins, callbacks, and task-function dispatch.

## Control Flow
Tasks are created inside transactions with reserved parameters such as type, priority, version, done future, validation key, and block ID. Executors poll available task subspaces, move tasks to active/timeout state, execute non-transactional `TaskFuncBase::execute`, then call transactional `finish`, which is intended to run exactly once. Long-running tasks periodically call `keepRunning` or extend timeouts. Futures can schedule follow-up tasks when set, allowing task graphs to be built transactionally.

## State and Persistence Behavior
All task queue state is persisted below the configured `Subspace`, including available, prioritized, active, timeout, pause, future, block, and callback keys. Task execution side effects are at least once; finish database mutations are designed to be exactly once for a task. Access to system keys and lock-aware options is configurable per bucket and future bucket.

## Dependencies and Integration Points
It depends on Flow futures, dispatched factories, generic actors, `NativeAPI.actor.h`, RYW transactions, `Subspace`, and `KeyBackedTypes`. It integrates with background management workflows that need persistent task queues, including backup, restore, data movement, and other long-running database jobs.

## Risks and Edge Cases
Task execution can be duplicated if an executor loses contact or misses timeout extension, so `execute` implementations must be idempotent or check `keepRunning`. `finish` must avoid long external side effects because it is the exactly-once transactional boundary. Priority compatibility is delicate because priority 0 uses the legacy `available` subspace. Validation keys can interrupt tasks unexpectedly if changed by other actors.

## Test Signals
Signals include task lifecycle tests, timeout/retry tests, future join/callback tests, pause/resume behavior, prioritized task ordering, validation-key interruption, and simulated executor failures during execute and finish.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TaskBucket.h -->
