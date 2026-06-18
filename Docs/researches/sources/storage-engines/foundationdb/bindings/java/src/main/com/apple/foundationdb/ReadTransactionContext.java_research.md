# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ReadTransactionContext.java

## Purpose
`ReadTransactionContext` abstracts objects that can execute read-only transactional functions, including `Database`, `Transaction`, and snapshot/read transaction views.

## Important APIs, Types, And Functions
It defines synchronous `read(Function<? super ReadTransaction,T>)`, asynchronous `readAsync(Function<? super ReadTransaction, ? extends CompletableFuture<T>>)` and `getExecutor()`.

## Control Flow
Concrete database contexts create retrying transactions; transaction contexts execute the function directly on the existing transaction; async variants return or compose `CompletableFuture`s.

## State And Persistence Behavior
The interface stores no state. Implementations decide whether a new transaction is created and retried or existing transaction state is used.

## Dependencies And Integration Points
It is extended by `ReadTransaction`, `TransactionContext`, and `Database`, and it uses Java `Function`, `CompletableFuture`, and `Executor`.

## Risks And Edge Cases
Code written against this abstraction may not know whether it is inside a retry loop or a single transaction. User functions must be safe under the concrete context's retry behavior.

## Test Signals
Tests should verify database retrying versus transaction direct execution, async exception wrapping, and executor propagation.
