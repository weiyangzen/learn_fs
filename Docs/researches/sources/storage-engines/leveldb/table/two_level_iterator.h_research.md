# sources/storage-engines/leveldb/table/two_level_iterator.h

## Purpose
`two_level_iterator.h` declares the factory for composing an index iterator and block-iterator factory into a flat iterator.

## Important APIs, Types, and Functions
`NewTwoLevelIterator(Iterator* index_iter, Iterator* (*block_function)(void*, const ReadOptions&, const Slice&), void* arg, const ReadOptions& options)` owns `index_iter` and uses the callback to create owned data iterators.

## Control Flow
The returned iterator seeks the index first, then materializes block iterators lazily as movement crosses block boundaries.

## State, Dependencies, and Integration
It depends on `Iterator`, `ReadOptions`, and `Slice`. `Table::NewIterator` is the primary caller.

## Risks and Test Signals
Callback ownership and error propagation are the key API risks. Tests validate the factory through table iteration scenarios.
