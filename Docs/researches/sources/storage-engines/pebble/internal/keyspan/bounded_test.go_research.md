# sources/storage-engines/pebble/internal/keyspan/bounded_test.go

## Purpose
Tests `BoundedIter`, the span iterator wrapper that enforces lower/upper bounds and optional prefix constraints over a child `FragmentIterator`.

## Important APIs, Types, And Functions
`TestBoundedIter` uses datadriven commands `define`, `set-prefix`, and `iter`. It parses spans with `ParseSpan`, wraps a `NewIter` in `invalidatingIter`, initializes `BoundedIter.Init(cmp, split, inner, lower, upper, &hasPrefix, &prefix)`, and exercises commands through `RunIterCmd`.

## Control Flow
The test defines a reusable iterator over invalidating spans, mutates prefix state, then repeatedly applies bounds with `SetBounds` before running seek/next/prev scripts. This stresses absolute positioning, direction changes, and bound resets against spans whose backing storage is invalidated after each child operation.

## State And Persistence Behavior
Only in-memory test state is used: span slices, prefix flags, and a bytes buffer. There is no persistence or global mutation.

## Dependencies And Integration Points
Depends on `datadriven`, `testkeys.Comparer`, and package-local iterator test helpers. It indirectly validates the production bounded iterator, even though `bounded.go` is outside this work item.

## Risks And Edge Cases
The test is valuable for lifetime and prefix-boundary edge cases. Its coverage is only as complete as `testdata/bounded_iter`; behavior involving production comparers other than `testkeys` is not covered here.

## Test Signals
Failures indicate regressions in bounded span seeks, relative movement at bounds, prefix filtering, or use-after-invalidated-child-span assumptions.
