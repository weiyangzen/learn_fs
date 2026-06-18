# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/TransactionContext.java

## Purpose
`TransactionContext` abstracts objects capable of running read/write transactional functions, either by creating retrying database transactions or by executing inside an existing transaction.

## Important APIs, Types, And Functions
It extends `ReadTransactionContext` and defines `run(Function<? super Transaction,T>)` plus `runAsync(Function<? super Transaction, ? extends CompletableFuture<T>>)`.

## Control Flow
Database implementations wrap functions in retry/commit loops. Transaction implementations call the supplied function directly without automatic commit.

## State And Persistence Behavior
The interface stores no state. Concrete behavior depends on whether the context owns a transaction or is a transaction.

## Dependencies And Integration Points
It is implemented by `Database` and `Transaction`, allowing higher-level code to accept either a database or transaction context.

## Risks And Edge Cases
Ambiguity between retrying database context and direct transaction context can matter for side effects and commit timing. Async functions must return futures whose failures propagate correctly.

## Test Signals
Tests should cover generic helpers working against both database and transaction contexts, sync/async exception propagation, and executor use inherited from read context.
