# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentList.java

## Purpose
`TestRocksDbPersistentList` verifies the `RocksDbPersistentList` implementation of `PersistentList` against a real temporary RocksDB instance. It confirms append and iteration semantics, including duplicate preservation and insertion order.

## Important APIs, Types, and Functions
- `RocksDbPersistentList<String>` is instantiated with `ManagedRocksDB`, a dedicated `ColumnFamilyHandle`, `CodecRegistry`, and element class.
- `PersistentList.add` persists values.
- `PersistentList.iterator()` returns a `ClosableIterator<String>`.
- `ManagedDBOptions`, `ManagedColumnFamilyOptions`, and `ManagedRocksDB.open` manage RocksDB lifecycle.

## Control Flow
`@BeforeAll` creates a RocksDB database with the default column family under `@TempDir`. The test creates a separate column family, appends `["e1", "e2", "e3", "e1", "e2"]`, iterates the persistent list, and compares each emitted value to the same index in the original list. The column family is dropped and closed in `finally`.

## State and Persistence Behavior
Values are written into a RocksDB column family. Duplicate elements must remain as distinct list entries, and iteration must reflect insertion order. Resource cleanup closes DB options, column-family options, and the DB, and drops the test column family.

## Dependencies and Integration Points
The test depends on the HDDS managed RocksDB wrappers, `CodecRegistry` raw encoding, and the Ozone `ClosableIterator` abstraction. It provides test coverage for snapshot-diff supporting persistent data structures.

## Risks and Edge Cases
- It does not reopen the DB to verify durability across process/lifecycle boundaries.
- It covers only strings and sequential iteration, not empty lists, large lists, or concurrent writes.

## Test Signals
Passing asserts that persisted list entries can be appended and read back in exact order with duplicates intact.
