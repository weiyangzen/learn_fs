# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessSingleThr.toml

## Purpose
Baseline non-multithreaded correctness scenario with a small client count.

## Important APIs, types, and functions
Sets `multiThreaded = false`, `minClients = 1`, `maxClients = 3`, and runs `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
The tester avoids multi-threaded FDB client configuration and runs normal workload scheduling.

## State and persistence behavior
Persists only standard workload data.

## Dependencies and integration points
Validates baseline parser/executor/workload behavior without buggify or client-thread randomization.

## Risks and test signals
Simpler concurrency makes this useful for reproduction, while watch behavior still requires correct scheduler progress.
