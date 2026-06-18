# sources/storage-engines/leveldb/db/db_iter.h

## Purpose
This header declares the factory for creating a user-visible DB iterator over an internal iterator at a fixed sequence number.

## Important APIs, Types, And Functions
`NewDBIterator(DBImpl* db, const Comparator* user_key_comparator, Iterator* internal_iter, SequenceNumber sequence, uint32_t seed)` returns a heap-allocated `Iterator`. The caller transfers ownership of `internal_iter` to the returned iterator.

## Control Flow
There is no implementation in the header. The signature exposes the needed inputs: DB backpointer for read sampling, user comparator for key grouping, internal iterator for raw entries, snapshot sequence for visibility, and random seed for sampling period.

## State And Persistence Behavior
The header defines no state and no persistence behavior. Runtime state lives in `DBIter` in `db_iter.cc`, while persistent visibility is controlled by the supplied sequence number.

## Dependencies And Integration Points
It includes `dbformat.h` and `leveldb/db.h`, forward-declares `DBImpl`, and is consumed by `db_impl.cc`.

## Risks And Edge Cases
Callers must pass an internal iterator ordered by `InternalKeyComparator` and keep DB/comparator lifetimes valid for the iterator. Misusing the sequence number changes snapshot visibility.

## Test Signals
Coverage is indirect through public iterator tests in `db_test.cc` and randomized iterator comparison against `ModelDB`.
