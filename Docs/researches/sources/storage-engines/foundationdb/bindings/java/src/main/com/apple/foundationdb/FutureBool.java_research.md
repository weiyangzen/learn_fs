# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureBool.java

## Purpose
`FutureBool` adapts a native FoundationDB future returning a boolean into a Java `CompletableFuture<Boolean>`.

## Important APIs, Types, And Functions
The constructor passes the pointer to `NativeFuture` and registers the marshal callback on the supplied executor. `getIfDone_internal` calls native `FutureBool_get`.

## Control Flow
When the native future becomes ready, `NativeFuture.marshalWhenDone` invokes `FutureBool_get`, completes the Java future, and disposes the native future through the base `postMarshal`.

## State And Persistence Behavior
State is the inherited native future pointer until callback completion, cancellation, or close. No persistent state exists.

## Dependencies And Integration Points
It depends on `NativeFuture`, `Executor`, `FDBException`, and JNI support for boolean future extraction.

## Risks And Edge Cases
Callback registration must occur after subclass initialization. Closing before completion completes the future exceptionally. Native errors propagate as exceptional completion.

## Test Signals
Tests should cover successful true/false completion, native error propagation, cancellation forwarding, close-before-ready behavior, and executor callback execution.
