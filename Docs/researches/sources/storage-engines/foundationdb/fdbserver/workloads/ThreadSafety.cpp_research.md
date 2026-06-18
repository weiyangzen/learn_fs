# sources/storage-engines/foundationdb/fdbserver/workloads/ThreadSafety.cpp

## Purpose
`ThreadSafetyWorkload` stress-tests FoundationDB thread-safe client APIs by sharing a transaction across multiple native threads that perform random operations and synchronized commits.

## Important APIs, Types, and Functions
The file defines `ThreadInfo`, a custom `Barrier`, and `ThreadSafetyWorkload`. It uses `ThreadSafeDatabase::createFromExistingDatabase()`, optional `MultiVersionDatabase::debugCreateFromExistingDatabase()`, `IDatabase`, `ITransaction`, `ThreadFuture`, `unsafeThreadFutureToFuture()`, `g_network->startThread()`, `onMainThreadVoid()`, Flow `Mutex`, and blocking thread methods such as `getBlocking()`.

## Control Flow
`start()` creates a thread-safe database wrapper, optionally wraps it in the multi-version API, spawns `threadsPerClient` worker threads, sleeps for `threadDuration`, sets `stopped`, then waits for each thread's `done` promise. Each thread calls `runTest()`: create or reuse a shared transaction, perform random sets, gets, key selectors, ranges, and clears, wait at a commit barrier, have one thread start `tr->commit()`, copy the `ThreadFuture` under mutex, wait for commit, synchronize again, clear the commit future, and exit when stopped.

## State and Persistence Behavior
Database state consists of random `ThreadSafetyKey%010d` keys set and cleared by shared transactions. Runtime state includes a shared transaction reference, shared commit future, mutex-protected stop flag, and barrier counters/events.

## Dependencies and Integration Points
This workload directly integrates with the FDB thread-safe API, multi-version API selection, network thread spawning, Flow synchronization primitives, and the tester framework. It sets `noUnseed = true` because thread scheduling makes the test intentionally nondeterministic.

## Risks and Edge Cases
The shared `ITransaction` is used by multiple threads, which is exactly the behavior under test. `Barrier::fire()` is called while holding the mutex in some paths and resets `numReached`; errors or early thread exits require `decrementNumRequired()` to avoid deadlock. Random operation exceptions are swallowed until commit, so some API failures only affect the transaction state. The workload reports thread errors through `success = false` and trace events.

## Test Signals
`check()` returns the `success` flag. Thread failures print to stdout and trace `ThreadSafety_ThreadFailed`. Absence of deadlock and completion after `threadDuration` are also essential signals.
