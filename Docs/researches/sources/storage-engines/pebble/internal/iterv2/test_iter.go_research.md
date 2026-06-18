# sources/storage-engines/pebble/internal/iterv2/test_iter.go

## Purpose
`test_iter.go` implements `TestIter`, a simple reference `iterv2.Iter` that precomputes a flat sequence of point and boundary entries from known points/spans for differential testing.

## Important APIs, Types, And Functions
`testEntry` records an `InternalKV`, region index, and directional skip flags. `TestIter` stores immutable input points/spans/bounds plus computed boundaries, region keys, entries, index, direction, current KV/span, prefix filter, and last seek mode. `TestIterData` is the input model. `NewTestIter`, `init`, `emitEntry`, `emitForward`, `emitBackward`, seek helpers, and all `Iter` methods implement the model.

## Control Flow
`init` clips points/spans to dynamic bounds, builds sorted/deduplicated boundaries from bounds, span endpoints, and extra boundaries, assigns span keys to regions, creates point and forward/backward boundary entries, and stable-sorts by internal key order. Forward methods skip entries marked `skipFwd` and optional prefix filters; backward methods skip `skipBwd`. Prefix seeking installs a filter that allows matching-prefix entries and the terminal nonmatching boundary needed by the iterv2 contract.

## State And Persistence Behavior
State is in-memory reference iterator position. `SetBounds` rebuilds computed entries. Values for SET keys are synthetic in random point generation, but `TestIter` mostly compares keys and spans.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `testkeys`, `treesteps`, `slices`, `sort`, and `errors`. It is the oracle for `CheckIter`, `InterleavingIter`, `SingleSpanIter`, and other span-aware iterators.

## Risks And Edge Cases
Because it is the oracle, bugs here can validate incorrect implementations. Prefix `TrySeekUsingNext` backtracking rules are intentionally special and only check reference-model sanity; `OpCheckIter` enforces the full legality contract.

## Test Signals
`test_iter_test.go` validates examples using shared datadriven input. Random tests using `CheckIter` indirectly stress this model continuously.
