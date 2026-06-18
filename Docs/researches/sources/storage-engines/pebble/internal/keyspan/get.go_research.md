# sources/storage-engines/pebble/internal/keyspan/get.go

## Purpose
Provides a small helper for locating the span covering a specific user key in a fragmented, non-overlapping span iterator.

## Important APIs, Types, And Functions
`Get(cmp, iter, key)` calls `iter.SeekGE(key)` and returns the span only if the found span's start is not greater than the target key.

## Control Flow
`SeekGE` finds the first span whose end is greater than `key`. `Get` then rejects the result if the span starts after `key`, because such a span is merely the next span, not a covering span. Errors are returned directly.

## State And Persistence Behavior
The helper mutates only the iterator position. It has no buffers or persistence and returns a child-owned span with normal iterator lifetime.

## Dependencies And Integration Points
Depends on `base.Compare` and `FragmentIterator`. It is used by tests and range tombstone/key lookup paths that need point containment over fragmented spans.

## Risks And Edge Cases
Correctness relies on non-overlapping fragmented spans and the `SeekGE` contract. A caller that reuses the returned span after moving the iterator can observe invalid data.

## Test Signals
`get_test.go` exercises present/absent keys and probe-injected errors.
