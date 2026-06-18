# sources/storage-engines/pebble/internal/iterv2/invalidating_iter.go

## Purpose
`invalidating_iter.go` wraps an `iterv2.Iter` to detect unsafe retention of returned key/value/span buffers by cloning results and corrupting previous clones on subsequent operations.

## Important APIs, Types, And Functions
`InvalidatingIter` stores the inner `Iter`, the last copied `InternalKV`, and a copied `Span`. `NewInvalidating` constructs the wrapper. `MaybeWrapInInvalidating` randomly wraps in invariant builds. `update` copies the inner result and span. `trashLast` corrupts previous key/value and span boundary/key buffers. The wrapper implements all `Iter` methods by delegation through `update` where appropriate.

## Control Flow
Every positioning method calls the inner iterator, then `update`. `update` first trashes prior copies, then deep-copies the current span boundary, span keys, suffixes, values, key, lazy value, and lazy fetcher. Nil results clear `lastKV` but still copy the inner span state.

## State And Persistence Behavior
All state is wrapper-local. Trashed copies are intentionally invalidated; callers must not depend on data after moving the iterator.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `invariants`, `treesteps`, `context`, and `slices`. It is used in randomized iterv2 tests and invariant builds.

## Risks And Edge Cases
Because `Span` returns a stable pointer to the wrapper’s copied span, callers stashing that pointer will see it mutated/trash-updated on later operations, matching iterator contract expectations. It does not alter errors or close behavior.

## Test Signals
Indirect tests wrap iterators randomly and compare behavior; failures usually indicate retained slices or incomplete deep-copy/trash coverage.
