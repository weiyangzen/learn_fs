# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessBlocking.toml

## Purpose
Runs API, atomic operation, and watch correctness workloads using blocking future waits.

## Important APIs, types, and functions
Enables `blockOnFutures`, `multiThreaded`, and `buggify`, then runs `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
The tester randomizes ranges and may raise client thread count to avoid blocking-mode self-deadlock.

## State and persistence behavior
Persists correctness, atomic, and watch workload key spaces in the cluster.

## Dependencies and integration points
Exercises `BlockingTransactionContext`, core FDB wrapper operations, workload factories, and retry behavior.

## Risks and test signals
Deadlock, atomic encoding errors, and watch non-delivery are key risks. A clean tester exit is the signal.
