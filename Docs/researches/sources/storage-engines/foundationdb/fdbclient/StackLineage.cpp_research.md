# sources/storage-engines/foundationdb/fdbclient/StackLineage.cpp

## Purpose
`StackLineage.cpp` exposes a small helper for retrieving the current Flow actor stack lineage as a vector of actor-name `StringRef`s. It is part of the actor lineage/profiling support used to report or inspect where execution is within nested actor contexts.

## Important APIs, types, and functions
The file includes `fdbclient/StackLineage.h` and defines `getActorStackTrace()`. The function dereferences the thread-local `currentLineage` pointer and calls `stack(&StackLineage::actorName)`, returning the lineage stack for the `StackLineage` property. A `StackLineageCollector` instantiation is present only as commented-out code in an anonymous namespace.

## Control flow
There is no asynchronous control flow. Callers synchronously invoke `getActorStackTrace()`, which walks the current lineage object through the Flow lineage API and returns the collected actor-name stack.

## State and persistence behavior
No persistent state is written. The function reads the thread-local lineage maintained by Flow (`currentLineage`) and returns references owned by lineage data. The commented collector means this translation unit currently does not register an additional collector at static initialization.

## Dependencies and integration points
The helper depends on Flow lineage primitives declared in `flow/flow.h` and the `StackLineage` property declared in `StackLineage.h`. `fdbserver/SigStack.cpp` calls `getActorStackTrace()` when producing signal stack diagnostics. Flow actor/coroutine code updates `currentLineage`, while actor lineage profiler code can use related lineage references.

## Risks and edge cases
Correctness relies on `currentLineage` being initialized for the calling thread and on lineage entries remaining valid for the returned `StringRef` vector. If actor compiler lineage annotation is disabled or not populated, the returned stack may be empty or less useful. Because the collector is commented out, any expected automatic collection behavior must come from other registration paths, not this file.

## Test signals
Useful checks are signal-stack diagnostics that include actor names, unit or integration tests that run nested Flow actors and assert `getActorStackTrace()` returns the expected order, and actor-lineage/profiler smoke tests that verify lineage remains available across coroutine boundaries.
