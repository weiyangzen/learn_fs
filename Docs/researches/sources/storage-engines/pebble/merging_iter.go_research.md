# sources/storage-engines/pebble/merging_iter.go

## Purpose
`merging_iter.go` implements Pebble's legacy `mergingIter`, a `base.InternalIterator` that merges multiple ordered child iterators from the LSM into one ordered point-key stream. It handles forward and reverse iteration, snapshot and batch snapshot visibility, prefix seeks, iterator bounds, range deletion shadowing, stats collection, and treesteps/debug integration.

## Important APIs, types, and functions
The central state is `mergingIter`, with `levels []mergingIterLevel`, a `mergingIterHeap`, direction `dir`, sequence visibility fields, bounds, prefix state, and `err`. `mergingIterLevel` couples a point iterator with the current `iterKV`, optional `rangeDelIter`, cached tombstone, generation counter, and optional backing `levelIter`.

Construction flows through `newMergingIter` and `(*mergingIter).init`. Public iterator methods are `SeekGE`, `SeekPrefixGE`, `SeekPrefixGEStrict`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, `Prev`, `Error`, `Close`, `SetBounds`, and `SetContext`. Core internal helpers include `seekGE`, `seekLT`, `nextEntry`, `prevEntry`, `findNextEntry`, `findPrevEntry`, `isNextEntryDeleted`, `isPrevEntryDeleted`, and direction-switch helpers `switchToMinHeap` and `switchToMaxHeap`.

## Control flow and state behavior
The iterator keeps one cached key per level. Positioning methods seek every relevant child iterator, build a min or max heap, then call `findNextEntry` or `findPrevEntry` to skip hidden entries. `Next` and `Prev` advance only the current heap root and repair the heap. Direction switches must reposition all levels past the current key so the same internal key is not returned twice.

Range deletion handling is lazy and level-aware. Range deletion iterators are positioned only for levels up to the current heap root. Higher-level tombstones can force lower levels to seek to tombstone bounds; same-level tombstones require sequence-number checks through `CoversAt`. `levelIter` range deletion generation changes force tombstone cache refreshes when table boundaries are crossed. Prefix iteration additionally prevents child iterators from advancing beyond the active prefix, especially under `TrySeekUsingNext`.

State is in-memory iterator state only. Persistence is through underlying sstable/memtable/batch iterators, while this file owns transient heap entries, tombstone caches, stats, and copied seek buffers. `Close` closes child iterators and range deletion iterators.

## Dependencies and integration points
This code integrates with `base.InternalIterator`, `levelIter`, `keyspan.FragmentIterator`, `base.InternalIteratorStats`, `combinedIterState`, `treesteps`, `invariants`, and Pebble comparer/split functions. It is the merge layer used above memtables, batches, L0 sublevels, and L1+ level iterators.

## Risks and test signals
High-risk areas are range tombstone positioning across table boundaries, direction switching, prefix-mode interaction with `TrySeekUsingNext`, sentinel-key handling, and preserving the `InternalIterator` error contract. Test coverage comes from datadriven tests in `merging_iter_test.go`, heap tests in `merging_iter_heap_test.go`, treesteps data, benchmarks for seek/next/prev locality, and broader metamorphic iterator workloads.
