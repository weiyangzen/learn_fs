# sources/storage-engines/pebble/internal/keyspan/keyspanimpl/merging_iter_test.go

## Purpose
Tests `MergingIter` behavior and its equivalence to eager fragmentation.

## Important APIs, Types, And Functions
`TestMergingIter` parses datadriven levels separated by `--`, wraps child `NewIter`s with `NewInvalidatingIter`, optionally attaches probes, and initializes `MergingIter` with `VisibleTransform(snapshot)`. `TestMergingIter_FragmenterEquivalence` and `_Seed` generate random levels, fragment all spans with `Fragmenter`, and compare random operations.

## Control Flow
The datadriven test defines child levels and runs iterator scripts. The randomized test builds sparse non-overlapping fragments per level, constructs both a reference `Iter` over eager fragments and a `MergingIter` over per-level iterators, positions both, and executes weighted random first/last/seek/next/prev operations.

## State And Persistence Behavior
Only in-memory levels, buffers, and random seeds are used. Child iterators deliberately invalidate spans to catch lifetime bugs.

## Dependencies And Integration Points
Depends on `datadriven`, `testkeys`, `keyspan.Fragmenter`, `VisibleTransform`, `NewInvalidatingIter`, and `require`.

## Risks And Edge Cases
Randomized generation covers many boundary layouts but mostly `RANGEKEYSET` spans with generated sequence ordering. Datadriven probes are needed for child error paths.

## Test Signals
Failures indicate mismatch between lazy merging and eager fragmentation, incorrect visibility filtering, boundary lifetime bugs, or seek/direction-switch errors.
