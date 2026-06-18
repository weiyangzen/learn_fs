# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentMap.java

## Purpose
`TestRocksDbPersistentMap` validates the RocksDB-backed `PersistentMap` implementation for basic put/get behavior and bounded iteration. It is used by snapshot diff tables and report/job persistence paths.

## Important APIs, Types, and Functions
- `RocksDbPersistentMap<String, String>` implements `PersistentMap`.
- `put`, `get`, and `iterator(Optional<K> lowerBound, Optional<K> upperBound)` are tested.
- `CodecRegistry` encodes keys and values.
- Parameterized `rocksDBPersistentMapIteratorCases()` supplies lower/upper-bound scenarios.

## Control Flow
The class initializes one RocksDB database for all tests and creates unique column families with an atomic id. `testRocksDBPersistentMap` writes repeated keys with newer values and verifies the final map value for each unique key. The parameterized iterator test loads sparse sorted key ranges, creates an iterator with optional bounds, and checks emitted entries against expected lexicographic ranges.

## State and Persistence Behavior
The map persists serialized keys and values in RocksDB. Duplicate `put` operations overwrite existing key values. Iterator behavior follows RocksDB key ordering and respects lower and upper bounds, with the upper bound treated as exclusive in the expected cases.

## Dependencies and Integration Points
This test uses RocksDB column families through managed wrappers and `ClosableIterator<Map.Entry<K,V>>`. Snapshot diff job/report storage uses the same persistent-map abstraction.

## Risks and Edge Cases
- Iterators are not explicitly closed in the parameterized test, which is acceptable for this small scope but worth watching in resource-sensitive paths.
- Tests cover strings only and do not verify deletion, null handling, binary keys, or reopening.

## Test Signals
Passing indicates map overwrites, reads, and bounded sorted iteration work for snapshot persistent-map use cases.
