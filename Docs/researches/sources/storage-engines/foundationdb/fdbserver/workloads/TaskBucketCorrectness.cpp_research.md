# sources/storage-engines/foundationdb/fdbserver/workloads/TaskBucketCorrectness.cpp

## Purpose
This source validates `TaskBucket`, `FutureBucket`, task chaining, and tuple `Subspace` behavior. It defines task functions that create and complete dependent tasks, plus a workload that drains the task bucket and checks expected side-effect keys.

## Important APIs, Types, and Functions
Task types are `SayHelloTaskFunc`, `SayHelloToEveryoneTaskFunc`, and `SaidHelloTaskFunc`, registered with `REGISTER_TASKFUNC`. The workload `TaskBucketCorrectnessWorkload` uses `TaskBucket`, `FutureBucket`, `Task`, `TaskFuture`, `ReadYourWritesTransaction`, `runRYWTransaction()`, and `Subspace`. It also defines a `TEST_CASE("/fdbclient/TaskBucket/Subspace")` for tuple/subspace packing, range, get, and unpack semantics.

## Control Flow
Client 0 clears `backup-agent/tasks` and `backup-agent/futures`, adds an initial `SayHelloToEveryone` task with an all-done future, and schedules a `SaidHello` task when that future is set. All clients repeatedly call `taskBucket->doOne()`. If no task is done, they check whether task and future buckets are empty; if both are empty, they exit. `check()` reads `Hello_` keys and verifies that the values exactly match `Hello, Everyone!`, `Said hello to everyone!`, and `task_0..task_n`.

## State and Persistence Behavior
Persistent state includes task bucket keys under `backup-agent/tasks`, future bucket keys under `backup-agent/futures`, the `addedInitTasks` guard key, and result keys with prefix `Hello_`. Task functions mutate task/future state in the caller transaction, then write result values. Chained mode creates one subtask at a time; non-chained mode creates all `SayHello` subtasks from the parent.

## Dependencies and Integration Points
The workload integrates with the FDB task bucket framework used by backup-agent style task scheduling, RYW transactions, tuple encoding, Flow unit tests, and tester workload registration.

## Risks and Edge Cases
The task functions call `finish()` before writing side-effect keys, so failures after finishing but before commit are handled transactionally only because all operations share the same transaction. A `buggify()` delay in `SayHelloTaskFunc::_finish()` can expose races. `start()` catches errors and calls `tr->onError()` once, but does not loop around the entire workload after an outer error. The subspace test prints to stdout and uses binary string comparisons, which are sensitive to tuple encoding changes.

## Test Signals
Trace events include `TaskBucketCorrectness`, `TaskBucketCorrectnessSayHello`, and `CheckSayHello`. The workload check returns false on count or data mismatch. The embedded unit test uses `ASSERT` for subspace behavior.
