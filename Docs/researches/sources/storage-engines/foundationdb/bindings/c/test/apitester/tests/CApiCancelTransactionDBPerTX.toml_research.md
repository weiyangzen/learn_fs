# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionDBPerTX.toml

## Purpose
Tests cancellation while creating a separate database handle for each transaction.

## Important APIs, types, and functions
Enables `databasePerTransaction`, `multiThreaded`, and `buggify`; runs standard `CancelTransaction` workload parameters.

## Control flow
Every transaction selects a fresh `fdb::Database`, increasing lifecycle churn while cancellation paths run.

## State and persistence behavior
Workload data persists in FDB; client state includes many short-lived database/transaction wrappers.

## Dependencies and integration points
Targets `DBPerTransactionExecutor`, FDB database lifecycle, and cancellation cleanup.

## Risks and test signals
Database handle leaks and callbacks referencing destroyed transactions are key risks. Passing under buggify validates lifecycle cleanup.
