# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTransactionExecutor.cpp

## Purpose
Implements the transaction lifecycle for API tester workloads: database selection, transaction creation, future continuations, retry handling, timeout restarts, and cluster-file/database-create fault injection.

## Important APIs, types, and functions
`TransactionContextBase` implements `ITransactionContext` with a `TxState` state machine, `commit`, `done`, `onError`, retry accounting, and transaction recreation. `BlockingTransactionContext` waits on futures on scheduler threads. `AsyncTransactionContext` registers FDB callbacks and tracks pending futures in `callbackMap`. `TransactionExecutorBase`, `DBPoolTransactionExecutor`, and `DBPerTransactionExecutor` configure temp cluster files and database selection.

## Control flow
`execute` creates a context, starts the workload lambda, and finishes via success continuation or `onError`. Retryable transactional errors go through `tx.onError`; non-transactional retryable errors restart directly; injected create errors and timeouts can recreate database/transaction state.

## State and persistence behavior
State includes FDB database/transaction wrappers, callback maps, retry history, temp cluster files, and an optional tamper thread. Temp files live under `tmpDir` and are deleted by `TmpFile`.

## Dependencies and integration points
Depends on `test/fdb_api.hpp`, `TesterScheduler`, `TesterUtil`, FDB error codes, filesystem, threads, and random helpers. It is the only FDB transaction access path for `WorkloadBase`.

## Risks and test signals
Risks include callback lifetime races, late cancelled futures, blocking-mode deadlock, retry loops, and scheduler destruction during callbacks. Signals include cancel/timeout/TLS/tamper TOML suites, retry-limit logs, and long-future wait logs.
