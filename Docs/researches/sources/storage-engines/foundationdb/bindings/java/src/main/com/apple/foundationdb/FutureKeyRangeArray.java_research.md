# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKeyRangeArray.java

## Purpose
`FutureKeyRangeArray` adapts native futures returning arrays of `Range` values into Java `CompletableFuture<KeyRangeArrayResult>`.

## Important APIs, Types, And Functions
It extends `NativeFuture<KeyRangeArrayResult>` and calls native `FutureKeyRangeArray_get`.

## Control Flow
The base callback machinery waits for native readiness, invokes the typed getter, completes the Java future, and disposes the native handle.

## State And Persistence Behavior
State is the native pointer before completion and the `KeyRangeArrayResult` after completion.

## Dependencies And Integration Points
It depends on `KeyRangeArrayResult`; it is part of the binding's typed native-future family even if this subset does not show a direct creator.

## Risks And Edge Cases
Range array ownership and copying are JNI-sensitive. Because the class is package-private, accidental external misuse is limited.

## Test Signals
Tests should cover empty/ranged results, native error completion, cancellation, and `KeyRangeArrayResult` list behavior.
