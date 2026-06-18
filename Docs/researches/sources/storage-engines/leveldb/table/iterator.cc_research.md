# sources/storage-engines/leveldb/table/iterator.cc

## Purpose
`iterator.cc` implements base iterator cleanup chaining and helper constructors for empty/error iterators.

## Important APIs, Types, and Functions
`Iterator::Iterator`, `Iterator::~Iterator`, `RegisterCleanup`, anonymous `EmptyIterator`, `NewEmptyIterator`, and `NewErrorIterator` are defined here.

## Control Flow
Cleanup registration stores the first cleanup inline and additional cleanups as heap nodes. The destructor runs all registered callbacks and deletes extra cleanup nodes. `EmptyIterator` always reports invalid and returns either OK or a stored error status.

## State, Dependencies, and Integration
Iterator cleanup is used by table block iterators to delete uncached blocks or release cache handles. Empty/error iterators provide uniform behavior for malformed blocks, missing children, and zero-way merges.

## Risks and Test Signals
Cleanup callbacks must tolerate destructor-time execution and own exactly the resources they receive. Tests indirectly validate cleanup through table/cache lifetimes and error iterator paths.
