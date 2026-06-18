# sources/storage-engines/pebble/internal/keyspan/keyspanimpl/merging_iter.go

## Purpose
Implements `MergingIter`, the on-the-fly cross-level span merger/fragmenter that produces spans fragmented at every unique child boundary and sorted by trailer descending.

## Important APIs, Types, And Functions
`MergingIter.Init`, `AddLevel`, `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `SetContext`, `Close`, `DebugString`, and `WrapChildren` are the main methods. `MergingBuffers` stores reusable keys/levels/heap/boundary buffers. `mergingIterLevel` steps a child iterator through start/end boundary events. `mergingIterHeap`, `boundKey`, and `boundKind` maintain min/max heaps of boundary keys.

## Control Flow
Each child span is represented as two boundary positions. Forward iteration uses a min-heap, chooses the current root user key as `start`, advances past all equal roots to find the next unique `end`, then collects keys from levels positioned at fragment-end boundaries. Reverse iteration mirrors this with a max-heap and fragment-start boundaries. Seeks initially position children in the opposite direction to discover the boundary on the far side of the seek key, copy unstable boundary keys when needed, switch heap direction, and synthesize or skip spans until keys remain after transformation.

## State And Persistence Behavior
The iterator stores only current boundary keys, current `[start,end)` bounds, a reusable `span`, and reusable buffers. It points keys into child iterator memory and rebuilds `m.keys` on every synthesized interval. No persistent storage is modified; child iterators own table resources.

## Dependencies And Integration Points
Depends on `base.Comparer`, `keyspan.FragmentIterator`, `keyspan.Transformer`, `manifest.NumLevels`, invariants, and `treesteps`. It is the central range-key/range-delete merge layer used above per-level iterators and below higher public iterator logic.

## Risks And Edge Cases
This is high-risk code: seek partitioning must handle equal start/end boundaries exactly, direction switches must not move the logical current span, child iterator span lifetimes require copying some boundary keys, empty child spans versus generated empty gaps must be distinguished, and transforms may remove all keys. Heap ordering intentionally ignores bound kind, so equal-key loops must consume all entries with the same user key.

## Test Signals
`merging_iter_test.go` has datadriven multi-level scripts, probe-injected child behavior, snapshot visibility transforms, and randomized equivalence against eager `Fragmenter` output.
