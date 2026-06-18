# sources/storage-engines/badger/table/merge_iterator.go

## Purpose
This file implements a duplicate-suppressing merge iterator over multiple sorted `y.Iterator`s. It is used to merge overlapping table, level, or memtable iterator streams while choosing one value for duplicate keys and supporting forward or reverse traversal.

## Important APIs, Types, and Functions
- `MergeIterator` stores left/right merge tree nodes, the currently selected node (`small`), current key copy, and direction.
- Internal `node` wraps a `y.Iterator` and caches concrete `MergeIterator` or `ConcatIterator` pointers for faster calls.
- `node.setIterator`, `setKey`, `next`, `rewind`, and `seek` abstract over raw, merge, and concat iterators.
- `fix` enforces which child should be current and advances duplicate keys on the right side.
- `Next`, `Rewind`, `Seek`, `Valid`, `Key`, `Value`, and `Close` implement `y.Iterator`.
- `NewMergeIterator` recursively builds a balanced binary merge tree.

## Control Flow and State Behavior
The merge iterator compares the selected node against the other node. In forward mode it keeps the smallest key; in reverse mode it keeps the largest key. When both keys compare equal, `fix` advances the right iterator and may swap selected nodes. `Next` also skips any key equal to the previously emitted `curKey`, so repeated duplicates within one child are suppressed.

`Rewind` and `Seek` reposition both children, call `fix`, and copy the selected key into `curKey`. `Value` delegates to the currently selected iterator. The recursive constructor returns nil for zero iterators, the original iterator for one, and nested merge iterators for larger sets.

## Dependencies and Integration Points
The implementation depends only on `bytes` and Badger `y.Iterator`/`CompareKeys`, with fast paths for `MergeIterator` and `ConcatIterator`. It is central to composing level/memtable views where newer sources should appear earlier in iterator ordering to win duplicate suppression.

## Risks and Edge Cases
Duplicate winner semantics depend on iterator ordering. In forward duplicates, the left side wins; in reverse, tests show the winner can be the later duplicate within the selected iterator due to reverse traversal. `Valid` assumes `small` has been initialized by `Rewind` or `Seek`; callers should position before use. `Close` closes both child iterators and wraps errors.

## Test Signals
`merge_iterator_test.go` covers zero/single/nested/many iterators, duplicates within and across iterators, forward/reverse seek, invalid seeks, close-count ownership, and winner behavior.
