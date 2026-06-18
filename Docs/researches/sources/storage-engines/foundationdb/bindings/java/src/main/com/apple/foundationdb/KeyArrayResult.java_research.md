# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyArrayResult.java

## Purpose
`KeyArrayResult` is a Java value container for native results encoded as concatenated key bytes plus per-key lengths.

## Important APIs, Types, And Functions
The constructor splits `keyBytes` according to `keyLengths` and populates `keys`. `getKeys()` returns the internal list.

## Control Flow
JNI constructs or passes data to this constructor for APIs such as range split points. The constructor walks length metadata, copies each segment, and appends it to the result list.

## State And Persistence Behavior
The object stores copied byte arrays in an in-memory `ArrayList`. The returned list is mutable and not defensively copied.

## Dependencies And Integration Points
It is returned by `FutureKeyArray` and `ReadTransaction.getRangeSplitPoints`.

## Risks And Edge Cases
Malformed lengths can overrun `keyBytes` and throw array-copy exceptions. Exposing the mutable list allows callers to mutate the result container.

## Test Signals
Tests should cover empty arrays, multiple keys, zero-length keys, malformed length totals, and list mutability expectations.
