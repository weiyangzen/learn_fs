# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessMultiThr.toml

## Purpose
Default broad multi-threaded buggified C API correctness scenario.

## Important APIs, types, and functions
Runs `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait` with randomized FDB/client/database/client ranges.

## Control flow
The tester enables multi-threaded FDB client behavior and buggify, then executes all workloads concurrently.

## State and persistence behavior
Persists random correctness data and watch keys. No TLS or special server config is present.

## Dependencies and integration points
Used by shim tests as the default API workload and covers parser, main tester, scheduler, executor, wrappers, and workload factories.

## Risks and test signals
Randomization broadens coverage but complicates reproduction. Clean exit and workload success logs are the signal.
