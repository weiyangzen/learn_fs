# sources/storage-engines/pebble/internal/keyspan/seek.go

## Purpose
Provides `SeekLE`, a helper to position a span iterator on the span covering or immediately before a target key.

## Important APIs, Types, And Functions
`SeekLE(cmp, iter, key)` uses the `FragmentIterator` interface and `base.Compare`.

## Control Flow
It first calls `SeekGE(key)`, which returns a covering span when one exists. If the result starts at or before the key, it is returned. Otherwise, it calls `Prev` to move to the largest span before the target.

## State And Persistence Behavior
The helper only repositions the iterator. It has no persistent state and returns child-owned span pointers.

## Dependencies And Integration Points
Used where span lookup needs predecessor semantics, including tests that apply visibility after seeking. It depends on correct `SeekGE` and `Prev` exhausted-state semantics.

## Risks And Edge Cases
If `SeekGE` returns nil after exhausting past the end, `Prev` is valid by interface contract and should return the last span. Errors from `SeekGE` are propagated, but errors from `Prev` are returned directly without additional context.

## Test Signals
`seek_test.go` compares `SeekLE` and raw `SeekGE` behavior over fragmented range-delete spans and probe-injected errors.
