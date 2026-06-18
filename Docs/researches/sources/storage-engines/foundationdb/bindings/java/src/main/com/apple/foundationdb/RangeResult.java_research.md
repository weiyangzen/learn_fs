# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResult.java

## Purpose
`RangeResult` is the package-private container for one normal range-query chunk and its `more` continuation flag.

## Important APIs, Types, And Functions
Constructors accept a test list, native concatenated key/value bytes with lengths, or a `RangeResultDirectBufferIterator`. `getSummary()` returns last key, key count, and `more`.

## Control Flow
Array-based native marshaling splits alternating key/value lengths into `KeyValue`s. Direct-buffer marshaling reads the summary and iterates rows. `RangeQuery` uses the summary to decide next fetch boundaries.

## State And Persistence Behavior
The result stores an in-memory list of copied `KeyValue`s and immutable `more`. The list can be mutated within the package.

## Dependencies And Integration Points
It depends on `KeyValue`, `RangeResultDirectBufferIterator`, and `RangeResultSummary`.

## Risks And Edge Cases
Odd length arrays throw `IllegalArgumentException`. Incorrect native length metadata can copy from wrong offsets. Continuation correctness depends on last-key ordering.

## Test Signals
Tests should cover empty chunks, odd length rejection, multi-row byte splitting, direct-buffer construction, and summary generation.
