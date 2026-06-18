# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResult.java

## Purpose
`MappedRangeResult` is the package-private container for one mapped-range result chunk and its continuation flag.

## Important APIs, Types, And Functions
Constructors accept either a `MappedKeyValue[]` or a `MappedRangeResultDirectBufferIterator`. `getSummary()` returns last key, row count, and `more`. `toString` prints values and continuation state.

## Control Flow
Native array marshaling constructs it directly. Direct-buffer marshaling calls `readResultsSummary`, iterates mapped rows, and stores them in a list. Range iterators use the summary to decide continuation selectors and termination.

## State And Persistence Behavior
The result stores a list of mapped values and immutable `more` flag. The list from `Arrays.asList` is fixed-size; the direct-buffer path uses a mutable `ArrayList`.

## Dependencies And Integration Points
It depends on `MappedKeyValue`, `MappedRangeResultDirectBufferIterator`, and `RangeResultSummary`.

## Risks And Edge Cases
`getSummary` uses the last returned key as continuation; wrong native ordering breaks iteration. Result list mutability differs between constructors.

## Test Signals
Tests should cover empty/non-empty summaries, `more` propagation, direct-buffer decoding, and constructor list behavior.
