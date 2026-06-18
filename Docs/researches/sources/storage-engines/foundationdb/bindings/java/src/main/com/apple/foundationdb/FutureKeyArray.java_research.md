# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKeyArray.java

## Purpose
`FutureKeyArray` adapts native futures returning an array of keys, currently used for range split points.

## Important APIs, Types, And Functions
It extends `NativeFuture<KeyArrayResult>`, registers a callback, and calls native `FutureKeyArray_get` from `getIfDone_internal`.

## Control Flow
After native readiness, the JNI layer returns a `KeyArrayResult`; the base future completes and disposes the native future.

## State And Persistence Behavior
Only the inherited pointer is mutable. Result data is copied into `KeyArrayResult`.

## Dependencies And Integration Points
It is created by `FDBTransaction.getRangeSplitPoints` and depends on `KeyArrayResult`.

## Risks And Edge Cases
Large split-point arrays can allocate many byte arrays. JNI length metadata must match concatenated key bytes.

## Test Signals
Tests should cover empty and multi-key results, native error propagation, and malformed JNI result handling through `KeyArrayResult` constructor tests.
