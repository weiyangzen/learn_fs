# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDBDatabase.java

## Purpose
`FDBDatabase` is the concrete native-backed implementation of `Database`. It owns the database pointer, creates native transactions, applies database options, and implements synchronous/asynchronous retry loops.

## Important APIs, Types, And Functions
It extends `NativeObjectWrapper` and implements `Database` plus `OptionConsumer`. Key methods are `run`, `runAsync`, `read`, `readAsync`, `createTransaction`, `setOption`, `getMainThreadBusyness`, `getClientStatus`, and `closeInternal`. Native methods create/dispose transactions, set database options, query busyness, and fetch client status.

## Control Flow
`run` creates a transaction, repeatedly invokes user logic, commits, and calls `onError` on runtime failures until success or non-retryable failure. `runAsync` performs the same loop with `AsyncUtil.whileTrue`, storing the final return value and closing the latest transaction in `whenComplete`. `createTransaction` locks the database pointer, wraps the native transaction, and sets used-during-commit protection compatibility options.

## State And Persistence Behavior
State includes the native database pointer, `DatabaseOptions`, executor, and optional `EventKeeper`. Closing disposes the native database once. Finalization warns and closes if the object is collected while still open.

## Dependencies And Integration Points
It depends on `FDBTransaction`, `NativeObjectWrapper`, `AsyncUtil`, `FutureKey`, `DatabaseOptions`, and native JNI database calls. `FDB.open` constructs it.

## Risks And Edge Cases
Retry loops may re-execute user code, so side effects outside FDB must be controlled. `runAsync` only routes `RuntimeException` through `onError`; other throwables become `CompletionException`. Finalizers are a last-resort leak detector and should not be relied on for cleanup.

## Test Signals
Tests should cover successful sync/async runs, retry after retryable commit/user errors, transaction closure after all paths, option forwarding under lock, client status future creation, and unclosed-resource warning behavior.
