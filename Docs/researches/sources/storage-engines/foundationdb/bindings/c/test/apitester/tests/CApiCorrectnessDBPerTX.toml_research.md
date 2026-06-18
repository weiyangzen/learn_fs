# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessDBPerTX.toml

## Purpose
Runs core correctness workloads with a fresh database handle for every transaction.

## Important APIs, types, and functions
Enables `databasePerTransaction`, `multiThreaded`, and `buggify`, running `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
Each transaction creates/selects a new database wrapper, then proceeds through normal async executor paths.

## State and persistence behavior
Correctness data persists in FDB; database handle lifecycle is client-side.

## Dependencies and integration points
Targets `DBPerTransactionExecutor`, RAII wrappers in `fdb_api.hpp`, and all core workloads.

## Risks and test signals
Lifecycle leaks and callbacks tied to destroyed handles are primary risks. Passing under buggify indicates robust handle cleanup.
