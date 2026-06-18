# sources/storage-engines/pebble/internal/keyspan/truncate.go

## Purpose
Implements `Truncate`, a `FragmentIterator` adapter that clips returned spans to user-key bounds and skips spans outside the bounds.

## Important APIs, Types, And Functions
`Truncate(cmp, iter, bounds)` returns a `truncatingIter`. The wrapper implements all fragment positioning methods, `SetContext`, `Close`, `WrapChildren`, and `TreeStepsNode`. `nextSpanWithinBounds` performs intersection and directional skipping.

## Control Flow
Each positioning method obtains a child span and calls `nextSpanWithinBounds` with direction. The helper rejects inclusive upper bounds that fall inside a span, intersects `[span.Start, span.End)` with `[bounds.Start, bounds.End.Key)`, returns original spans when unchanged, returns a reusable clipped span when the intersection is non-empty, or advances until a span intersects.

## State And Persistence Behavior
The wrapper stores one reusable clipped `Span` pointing at original key slices. It forwards context and close to the child. No persistent state is modified.

## Dependencies And Integration Points
Depends on `base.UserKeyBounds`, `invariants`, `treesteps`, and `FragmentIterator`. It is useful wherever table or user bounds need to be imposed on span iterators without changing the underlying source.

## Risks And Edge Cases
Seek methods perform an extra correction because clipping can move a span entirely before/after the search key. Inclusive upper bounds inside spans are assertion failures. Returned clipped spans borrow child key slices and are transient.

## Test Signals
`truncate_test.go` validates full truncation output and saved-iterator relative commands over datadriven range deletion spans.
