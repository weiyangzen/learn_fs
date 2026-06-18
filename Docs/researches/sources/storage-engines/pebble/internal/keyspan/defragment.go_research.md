# sources/storage-engines/pebble/internal/keyspan/defragment.go

## Purpose
Implements `DefragmentingIter`, a `FragmentIterator` adapter that joins adjacent physical span fragments back into wider logical spans when a caller-provided equality method says their state is equivalent.

## Important APIs, Types, And Functions
`DefragmentMethod` and `DefragmentMethodFunc` decide whether abutting spans may merge. `DefragmentInternal` compares trailer, suffix, and value equality in trailer-desc order. `DefragmentReducer` combines key slices, with `StaticDefragmentReducer` retaining the first fragment's keys. `DefragmentingBuffers.PrepareForReuse` caps retained buffers, and `DefragmentingIter.Init`, `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, and `Prev` implement iteration.

## Control Flow
Seeking may land in the middle of a logical span. `SeekGE` first seeks forward; if the landed fragment covers the seek key, it defragments backward to find the logical start, steps back onto the first fragment if necessary, then defragments forward. `SeekLT` mirrors this around the logical end. Direction switches use `iterPosPrev`, `iterPosCurr`, and `iterPosNext` to remember whether the child iterator is already positioned on a previous or next physical fragment. `defragmentForward` and `defragmentBackward` repeatedly check adjacency plus method equality, widen `curr.Start` or `curr.End`, and reduce keys.

## State And Persistence Behavior
The iterator keeps copied current span state in `curr`, `currBuf`, `keysBuf`, and `keyBuf` because child iterator spans are only stable until the next positioning call. It persists no on-disk data. Buffer reuse is bounded to avoid retaining unusually large byte/key allocations.

## Dependencies And Integration Points
Depends on `base.Comparer`, range suffix comparison, `bytealloc`, invariants checks, and `treesteps`. It integrates above any `FragmentIterator`, including `Iter`, `LevelIter`, and `MergingIter`, and is used when compactions or iterator stacks need to hide physical fragmentation created by sstable boundaries.

## Risks And Edge Cases
The key risks are off-by-one adjacency around exclusive ends, direction-switch bugs, equality methods that do not match key order assumptions, reducers that mutate `next`, and retaining child-backed slices without copying. Empty spans intentionally do not defragment to avoid unnecessary block loads.

## Test Signals
`defragment_test.go` covers datadriven iteration, probe-injected errors, static versus collecting reducers, an always-equal method, and randomized equivalence between original spans and deliberately fragmented spans.
