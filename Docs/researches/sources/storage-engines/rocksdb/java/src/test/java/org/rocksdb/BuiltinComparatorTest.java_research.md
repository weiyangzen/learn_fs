# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BuiltinComparatorTest.java

## Purpose
`BuiltinComparatorTest` verifies built-in bytewise and reverse-bytewise comparator behavior through real DB iteration.

## Important APIs and Types
Tests use `BuiltinComparator.BYTEWISE_COMPARATOR`, `BuiltinComparator.REVERSE_BYTEWISE_COMPARATOR`, `Options.setComparator`, `RocksDB`, and `RocksIterator`.

## Control Flow, State, and Persistence
Each comparator test opens a temp DB, writes keys `abc1` through `abc3`, iterates from first to end, checks key order and values, seeks to last, and checks seek behavior. The enum test verifies ordinal stability, value count, and `valueOf`.

## Dependencies and Integration Points
Depends on RocksDB native library, JUnit, AssertJ, temp folders, and DB iterator APIs.

## Risks and Test Signals
The tests protect comparator ordering and enum compatibility. They also confirm reverse comparator seek semantics differ from forward ordering. They do not test Java comparator implementations directly, but they provide baseline expectations for native built-ins referenced by util comparator docs.
