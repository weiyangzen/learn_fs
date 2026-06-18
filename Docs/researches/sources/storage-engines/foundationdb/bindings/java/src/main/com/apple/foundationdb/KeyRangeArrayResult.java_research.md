# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyRangeArrayResult.java

## Purpose
`KeyRangeArrayResult` wraps an array of `Range` objects returned by native calls into a list-oriented Java result object.

## Important APIs, Types, And Functions
The constructor stores `Arrays.asList(keyRangeArr)` in `keyRanges`. `getKeyRanges()` exposes that list.

## Control Flow
Native JNI code supplies a `Range[]`; Java code wraps it without copying individual ranges.

## State And Persistence Behavior
The list is fixed-size but backed by the original array. `Range` objects contain byte-array references and are not deeply copied here.

## Dependencies And Integration Points
It is returned by `FutureKeyRangeArray` and depends on `Range`.

## Risks And Edge Cases
Because the list is array-backed, changes to the original array would be visible if retained elsewhere. Range byte arrays are mutable by reference.

## Test Signals
Tests should cover empty and multi-range arrays, fixed-size list behavior, and equality of wrapped ranges.
