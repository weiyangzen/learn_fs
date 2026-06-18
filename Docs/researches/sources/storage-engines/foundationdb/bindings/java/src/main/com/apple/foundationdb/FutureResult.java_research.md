# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureResult.java

## Purpose
`FutureResult` adapts native futures returning a value byte array from point reads and records fetched-byte metrics.

## Important APIs, Types, And Functions
It extends `NativeFuture<byte[]>`, stores an optional `EventKeeper`, calls native `FutureResult_get`, and counts result bytes in `postMarshal`.

## Control Flow
`FDBTransaction.get` creates it. On native readiness, `NativeFuture` marshals the value, completes the Java future, calls `postMarshal`, and closes the native future.

## State And Persistence Behavior
The native pointer is held until completion/cancel/close. The marshaled value is a heap byte array or null for absent keys.

## Dependencies And Integration Points
It depends on `EventKeeper` and is the point-read counterpart of `FutureKey`.

## Risks And Edge Cases
Absent values produce null and no byte count. Large values allocate heap memory, while range queries may use direct buffers if enabled.

## Test Signals
Tests should cover present and absent values, byte accounting, native errors, cancellation, and explicit close.
