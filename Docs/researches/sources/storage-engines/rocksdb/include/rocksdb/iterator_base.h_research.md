# Research: sources/storage-engines/rocksdb/include/rocksdb/iterator_base.h

## Purpose

`iterator_base.h` declares `IteratorBase`, the minimal cleanable cursor interface shared by RocksDB iterators. It captures positioning, forward/backward movement, refresh, deferred value preparation, key access, and status reporting without prescribing value representation.

## Important APIs, Types, and Functions

`IteratorBase` inherits from `Cleanable` and declares pure virtual `Valid`, `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `Prev`, `key`, and `status`. It provides virtual defaults for `Refresh()`, `Refresh(const Snapshot*)`, and `PrepareValue()`. Copy and assignment are deleted. `Seek` and `SeekForPrev` accept user keys without timestamps.

## Control Flow

The expected control flow is seek, check `Valid()`, consume `key()` and subclass-specific value APIs, advance, and inspect `status()`. Seek methods clear prior error state so `status()` after a seek reflects only the seek and later movement. `Refresh()` invalidates the iterator and moves it to a latest DB state or a supplied snapshot, after which callers must seek again. `PrepareValue()` is called when `ReadOptions::allow_unprepared_value` let the iterator defer loading expensive values.

## State and Persistence Behavior

The interface owns no persistence. Concrete iterators may hold cleanup callbacks through `Cleanable`, DB version references, snapshots, file handles, pinned cache blocks, or deferred value state. `PrepareValue()` can change iterator validity and status if loading fails. `status()` may return `Status::Incomplete()` for non-blocking I/O paths that would need additional I/O.

## Dependencies and Integration Points

The header depends on `cleanable.h`, `slice.h`, and `status.h`, and forward-declares `Snapshot`. `Iterator` in `iterator.h` builds on it. Internal wrappers like `IteratorWrapper`, table readers, merge iterators, BlobDB, external table wrappers, and multi-column-family iterators rely on this base contract.

## Risks and Edge Cases

Callers must not call `Next`, `Prev`, or `key` unless `Valid()` is true. Refresh invalidates current positioning and can silently change snapshot semantics to the latest state when no snapshot is supplied. `allow_unprepared_value` requires applications or wrapper iterators to call `PrepareValue()` before accessing values; HISTORY entries note past incorrect values when wrappers failed to do so. Non-blocking I/O users must treat `Incomplete` as a state, not data absence.

## Test Signals

Relevant signals include iterator tests for refresh semantics, BlobDB and multi-column-family `PrepareValue()` behavior, table iterator status propagation, invalid-state assertions, and `Status::Incomplete()` handling in non-blocking paths. Existing HISTORY notes around `BaseDeltaIterator` and unprepared values are useful regression targets.
