# sources/storage-engines/pebble/internal/iterv2/interleaving_iter.go

## Purpose
`interleaving_iter.go` implements `iterv2.Iter` by combining a point `base.InternalIterator` with a `keyspan.FragmentIterator`, emitting point keys and synthetic span-boundary keys while exposing the current span.

## Important APIs, Types, And Functions
`InterleavingIter` stores comparers, point/span iterators, static range bounds, dynamic bounds, cached point/span positions, direction flags, boundary state, presented `Span`, prefix mode, error, and scratch buffer. Public methods include `Init`, `Span`, `InvalidateCachedSpan`, all internal iterator positioning methods, `SetBounds`, `Error`, `Close`, `SetContext`, `String`, and `TreeStepsNode`. Core helpers include `computeCurrentSpan`, `emitBoundary`, `positionSpanIterForward`, `positionSpanIterBackward`, `resolveForward`, `resolveBackward`, boundary update helpers, direction switch helpers, and invariant checks.

## Control Flow
Forward seeks position the point iterator, position or reuse the span iterator around the seek key, compute the presented span, and return whichever comes first: point key or boundary. `Next` advances point state or, after a boundary, enters the adjacent span/gap and recomputes. Reverse flow mirrors this with span starts. Direction switches reseek/advance to match internal iterator semantics. Prefix seeks restrict point results while still exposing the first relevant boundary needed to discover covering spans.

## State And Persistence Behavior
State is in-memory iterator position only. `presentedSpan` points into current span keys and is invalidated on exhaustion. `InvalidateCachedSpan` is an explicit escape hatch when the underlying span iterator has been reinitialized.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `invariants`, `treesteps`, `crstrings`, and `errors`. It is a central implementation of the span-aware iterator contract documented in `iter.go` and is used by merging/level iterator work.

## Risks And Edge Cases
Boundary ordering with point keys at the same user key is subtle. Prefix iteration must not hide range deletion spans that cover the prefix. Dynamic bounds forbid `First`/`Last` in invariant builds. `TrySeekUsingNext` reuse of span state must not reuse a span past its end.

## Test Signals
Datadriven tests in `interleaving_iter_test.go` cover scripted examples, while `interleaving_iter_rand_test.go` compares random operations against `TestIter` through `CheckIter`.
