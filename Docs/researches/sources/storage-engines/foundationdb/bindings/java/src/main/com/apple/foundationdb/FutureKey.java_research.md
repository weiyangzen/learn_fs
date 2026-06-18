# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKey.java

## Purpose
`FutureKey` adapts native futures that return a single key-like byte array and records fetched-byte instrumentation.

## Important APIs, Types, And Functions
It extends `NativeFuture<byte[]>`, stores an optional `EventKeeper`, calls native `FutureKey_get`, and overrides `postMarshal` to count `BYTES_FETCHED` when the result is non-null.

## Control Flow
Native readiness triggers byte-array extraction, Java future completion, byte counting, and native future disposal.

## State And Persistence Behavior
State consists of the inherited native pointer and an event keeper reference. The returned byte array is a Java copy from native memory.

## Dependencies And Integration Points
It is used for `getKey`, `getVersionstamp`, and database client status paths that return key/byte payloads. It depends on `EventKeeper.Events`.

## Risks And Edge Cases
Null values are not counted, which is correct for absent values but means diagnostics differ by result presence. Large keys/status payloads are fully copied into heap memory.

## Test Signals
Tests should verify value completion, byte-count increment, null result behavior, native errors, and close/cancel behavior inherited from `NativeFuture`.
