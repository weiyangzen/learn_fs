# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultSummary.java

## Purpose
`RangeResultSummary` packages the continuation-relevant metadata for a range chunk: last key, row count, and whether more data exists.

## Important APIs, Types, And Functions
Fields are `lastKey`, `keyCount`, and `more`. `toString` formats the last key with `ByteArrayUtil.printable`.

## Control Flow
`RangeResult` and `MappedRangeResult` produce summaries; range iterators consume them to decrement remaining row counts and update begin/end selectors.

## State And Persistence Behavior
The object is immutable by fields but stores a byte-array reference for `lastKey`.

## Dependencies And Integration Points
It is shared by normal and mapped range query implementations.

## Risks And Edge Cases
Null `lastKey` signals empty chunks and causes iterators to complete false. Mutating the last-key array after summary creation could alter debug output and continuation if reused.

## Test Signals
Tests should verify empty and non-empty summaries, `more` propagation, and printable formatting.
