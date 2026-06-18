# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureVoid.java

## Purpose
`FutureVoid` adapts native futures whose meaningful result is success or error, such as commit, watch, and transaction `onError`.

## Important APIs, Types, And Functions
It extends `NativeFuture<Void>` and implements `getIfDone_internal` by calling inherited native `Future_getError`; non-success errors are thrown, otherwise null is returned.

## Control Flow
Native readiness invokes error inspection, completes the Java future with null on success, and closes the native future through the base class.

## State And Persistence Behavior
The native pointer is held until completion, cancellation, or close. Completed value is always null.

## Dependencies And Integration Points
It is used by `FDBTransaction.commit`, `watch`, and `onError`.

## Risks And Edge Cases
Correctness depends on `Future_getError` distinguishing success from failure. Unknown-result commit errors propagate as exceptional completion and must be handled by retry loops.

## Test Signals
Tests should cover success, retryable and non-retryable errors, cancellation, close-before-ready, and use in `Transaction.onError`.
