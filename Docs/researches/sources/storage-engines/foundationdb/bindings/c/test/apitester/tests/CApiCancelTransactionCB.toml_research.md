# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionCB.toml

## Purpose
Callback-based cancel-transaction scenario for multi-threaded buggified clients.

## Important APIs, types, and functions
Leaves `blockOnFutures` false, so `AsyncTransactionContext` handles future callbacks. Configures `CancelTransaction` with key/value ranges, initial size, random operations, and read-existing ratio.

## Control flow
The tester randomizes concurrency and database pool settings, then runs cancellation through callback continuations.

## State and persistence behavior
Persists and mutates workload keys in the cluster; callback state is client-side.

## Dependencies and integration points
Exercises async executor callback maps, workload cancellation logic, and buggified FDB client behavior.

## Risks and test signals
Late cancelled callbacks, double completion, and object lifetime races are the main risks. Success is zero exit under randomized concurrency.
