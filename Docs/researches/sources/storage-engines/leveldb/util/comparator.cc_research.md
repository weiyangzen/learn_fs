# sources/storage-engines/leveldb/util/comparator.cc

## Purpose
`comparator.cc` implements the default bytewise key comparator and comparator destructor.

## Important APIs, Types, and Functions
`Comparator::~Comparator`, `BytewiseComparatorImpl::Name`, `Compare`, `FindShortestSeparator`, `FindShortSuccessor`, and `BytewiseComparator()` are defined here.

## Control Flow
Compare delegates to `Slice::compare`. `FindShortestSeparator` finds the first differing byte and increments it when the result remains below the limit. `FindShortSuccessor` increments the first non-0xff byte and truncates. `BytewiseComparator` returns a no-destructor singleton.

## State, Persistence, and Integration
Comparator names are part of DB/table compatibility checks elsewhere. Separator/successor shortening is used by `TableBuilder` to reduce index keys without violating ordering.

## Risks and Test Signals
Shortening must never produce a key outside the required range. Table tests with bytewise and reverse comparators validate seek behavior and index key handling.
