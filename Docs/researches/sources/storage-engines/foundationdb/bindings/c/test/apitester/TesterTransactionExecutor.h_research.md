# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTransactionExecutor.h

## Purpose
Declares the abstraction that lets workloads execute FDB operations without owning database, transaction, continuation, or retry mechanics.

## Important APIs, types, and functions
`ITransactionContext` exposes `db`, `dbOps`, `tx`, `continueAfter`, `continueAfterAll`, `commit`, `onError`, `done`, and `makeSelfConflicting`. `TransactionExecutorOptions` configures future mode, DB-per-transaction, injected database-create failures, cluster-file tampering, retry limit, and temp dir. `ITransactionExecutor` defines `init`, `execute`, `selectDatabase`, `getClusterFileForErrorInjection`, and `getOptions`.

## Control flow
Workloads pass start/final continuations to `execute` and attach FDB future continuations through the context. The implementation decides blocking versus callback behavior.

## State and persistence behavior
Only interfaces and config are declared. Runtime persistence is limited to ordinary committed FDB transactions plus implementation-owned temp files.

## Dependencies and integration points
Depends on `test/fdb_api.hpp`, `TesterOptions`, and `TesterScheduler`. It is the integration contract between workloads and the FDB C API wrapper.

## Risks and test signals
Misuse can happen if workloads call `done` too early or forget self-conflict protection for timeout-restarted writes. Compile-time signature drift and runtime correctness/cancel tests are the main signals.
