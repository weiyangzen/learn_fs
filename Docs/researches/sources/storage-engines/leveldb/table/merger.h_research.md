# sources/storage-engines/leveldb/table/merger.h

## Purpose
`merger.h` declares the sorted union iterator factory used by DB iteration.

## Important APIs, Types, and Functions
`NewMergingIterator(const Comparator*, Iterator** children, int n)` takes ownership of child iterators and returns an `Iterator`.

## Control Flow
The factory returns an empty iterator for no children, returns the sole child unchanged for one child, and otherwise constructs the merging iterator implementation.

## State, Dependencies, and Integration
It depends only on `Comparator` and `Iterator` declarations. It integrates with LevelDB's version/memtable iteration layers.

## Risks and Test Signals
The ownership contract is important, especially for the one-child fast path. Duplicate suppression is explicitly absent and must be handled elsewhere.
