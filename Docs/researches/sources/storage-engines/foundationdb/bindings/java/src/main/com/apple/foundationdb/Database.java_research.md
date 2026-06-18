# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Database.java

## Purpose
`Database` is the public interface for a FoundationDB database connection. It creates transactions, exposes database options/status, provides retry-loop transaction helpers, and defines the resource-close contract.

## Important APIs, Types, And Functions
The interface extends `AutoCloseable` and `TransactionContext`. Key methods are `createTransaction`, `options`, `getMainThreadBusyness`, synchronous/asynchronous `read` and `run` overloads, `close`, and `getClientStatus`. Default methods route no-executor overloads through `getExecutor`.

## Control Flow
Client code normally obtains a `Database` from `FDB.open`, then executes work through `run` or `runAsync`. Implementations create a transaction, call user logic, commit for mutating paths, and retry through `Transaction.onError` for retryable `FDBException`s.

## State And Persistence Behavior
The interface describes a native database resource that must be closed. No state is stored by the interface itself; `FDBDatabase` owns the native pointer, executor, options, and optional instrumentation.

## Dependencies And Integration Points
It integrates with `Transaction`, `ReadTransaction`, `TransactionContext`, `DatabaseOptions`, `EventKeeper`, Java `CompletableFuture`, `Executor`, and user-supplied `Function`s. `LocalityUtil` and retry helpers consume this interface.

## Risks And Edge Cases
Retryable blocks can execute multiple times after unknown commit results, so user code must be idempotent or otherwise safe. Failure to close databases leaks native resources. Custom executors can affect callback ordering and liveness.

## Test Signals
Tests should cover transaction creation, sync and async retry loops, read-only aliases, custom executor propagation, close idempotence through implementation, status retrieval, and exception propagation from user functions and commits.
