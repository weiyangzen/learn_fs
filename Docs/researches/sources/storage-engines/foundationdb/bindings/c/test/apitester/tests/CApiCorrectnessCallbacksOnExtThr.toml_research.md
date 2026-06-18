# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessCallbacksOnExtThr.toml

## Purpose
Validates correctness while FDB callbacks execute on external client threads.

## Important APIs, types, and functions
Sets `fdbCallbacksOnExternalThreads = true`, `multiThreaded = true`, `buggify = true`, and runs `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
The tester applies `FDB_NET_OPTION_CALLBACKS_ON_EXTERNAL_THREADS`; callbacks enter `AsyncTransactionContext` from external threads and are scheduled back to the local scheduler.

## State and persistence behavior
Persists standard correctness workload data; cross-thread callback state is in memory.

## Dependencies and integration points
Integrates multi-version client callback threading, async executor callback maps, and workload invariants.

## Risks and test signals
Main risks are race conditions, scheduler lifetime issues, and callback map misuse. Passing validates thread-safe callback handoff.
