# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiTamperClusterFile.toml

## Purpose
Tests recovery while the tester's cluster file is tampered from unreachable to invalid to valid.

## Important APIs, types, and functions
Sets `tamperClusterFile = true`, `multiThreaded = true`, `buggify = true`, and runs `ApiCorrectness`.

## Control flow
`TransactionExecutorBase` writes a synthetic cluster file, later invalidates it, and finally copies the real cluster file while transactions retry.

## State and persistence behavior
Mutates a temporary cluster file under `tmpDir` and persists workload data after recovery.

## Dependencies and integration points
Exercises cluster-file reload, database-create failure handling, transaction retry, and API correctness.

## Risks and test signals
Permanent initialization failure and retry storms are risks. Passing shows eventual recovery and workload completion.
