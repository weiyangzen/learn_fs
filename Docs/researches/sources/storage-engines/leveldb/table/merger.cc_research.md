# sources/storage-engines/leveldb/table/merger.cc

## Purpose
`merger.cc` implements an iterator that merges multiple sorted child iterators without duplicate suppression.

## Important APIs, Types, and Functions
`MergingIterator` implements `SeekToFirst`, `SeekToLast`, `Seek`, `Next`, `Prev`, `key`, `value`, and `status`. `FindSmallest` and `FindLargest` select the active child. `NewMergingIterator` handles zero-, one-, and many-child cases.

## Control Flow
Forward seeks position all children and choose the smallest key. Reverse seeks choose the largest. When changing direction, non-current children are repositioned around the current key so `Next` or `Prev` does not repeat entries. The current child advances, then the minimum/maximum child is recomputed by linear scan.

## State, Persistence, and Integration
State includes comparator, owned `IteratorWrapper` array, current child, child count, and direction. It is used by higher DB layers to merge memtables/SSTables; no durable state is written.

## Risks and Test Signals
Duplicate keys are intentionally yielded multiple times, so callers must do visibility/version suppression. Direction switching is subtle and covered indirectly by table and DB random-access iterator tests.
