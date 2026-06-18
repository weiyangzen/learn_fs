# sources/storage-engines/leveldb/table/iterator_wrapper.h

## Purpose
`iterator_wrapper.h` provides a small owning wrapper that caches `Valid()` and `key()` results from an underlying iterator.

## Important APIs, Types, and Functions
`IteratorWrapper` exposes `Set`, `iter`, `Valid`, `key`, `value`, `status`, navigation methods, and private `Update`.

## Control Flow
`Set` deletes the previous iterator and takes ownership of the new one. Navigation delegates to the underlying iterator then refreshes cached validity and key. Value and status remain delegated.

## State, Dependencies, and Integration
It stores an owned `Iterator*`, cached `valid_`, and cached `Slice key_`. `MergingIterator` and `TwoLevelIterator` use it to reduce virtual calls and simplify child iterator ownership.

## Risks and Test Signals
The cached key is a slice owned by the child iterator, so it must only be used while the child remains positioned and alive. Merging and table iterator tests exercise direction changes and child replacement.
