# sources/storage-engines/rocksdb/util/vector_iterator.h

## Purpose

Implements `VectorIterator`, an `InternalIterator` over in-memory vectors of key/value strings, optionally sorted by a supplied comparator.

## APIs, control flow, and state

Construction moves key/value vectors, asserts equal sizes, builds an index vector, and sorts indices when a comparator is supplied. `SeekToFirst`, `SeekToLast`, `Seek`, and `SeekForPrev` update `current_` using lower/upper bound over either raw sorted keys or comparator-sorted indices. `Next` and `Prev` adjust the index. `key` and `value` return slices into owned strings, `status` is always OK, and both key/value are reported pinned.

## Dependencies and integration

It depends on internal iterator, comparator, slice, and DB format headers. It is useful in tests and internal adapters that need an iterator facade over materialized data.

## Risks and test signals

There are no direct tests in this subset. Risks include unsigned underflow in `SeekToLast`/`Prev` on empty or before-first state, and the no-comparator path assumes input keys are already sorted in natural string order. Comparator path keeps storage stable through owned vectors and indirection.
