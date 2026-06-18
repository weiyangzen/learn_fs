# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureInt64.java

## Purpose
`FutureInt64` adapts native 64-bit integer futures, such as read versions, estimated sizes, and approximate transaction sizes, into Java `CompletableFuture<Long>`.

## Important APIs, Types, And Functions
It extends `NativeFuture<Long>`, registers a marshal callback in the constructor, and implements `getIfDone_internal` through native `FutureInt64_get`.

## Control Flow
Native readiness triggers callback execution on the provided executor; the base class reads the long, completes the Java future, and disposes the native handle.

## State And Persistence Behavior
Only the inherited native pointer is mutable. Completion value is stored by `CompletableFuture` after marshaling.

## Dependencies And Integration Points
It is used by `FDBTransaction.getReadVersion`, `getEstimatedRangeSizeBytes`, and `getApproximateSize`.

## Risks And Edge Cases
Native integer width and Java `long` mapping must match. Exceptional native futures must become `FDBException` completions.

## Test Signals
Tests should cover successful value completion, large positive values, native errors, cancellation, and explicit close.
