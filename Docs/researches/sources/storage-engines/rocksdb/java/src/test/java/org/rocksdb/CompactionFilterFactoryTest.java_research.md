# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionFilterFactoryTest.java

## Purpose

Tests that a Java compaction filter factory attached to `ColumnFamilyOptions` is invoked through native compaction for a column family.

## Important APIs, control flow, and dependencies

The test uses `RemoveEmptyValueCompactionFilterFactory`, `ColumnFamilyOptions.setCompactionFilterFactory`, `ColumnFamilyDescriptor`, `DBOptions`, `RocksDB.open`, `flush`, `compactRange`, and `keyMayExist`. It opens default plus `new_cf`, writes a normal value and an empty value to the filtered CF, flushes, compacts, and verifies the normal value remains while the empty value may not exist.

## State, persistence, risks, and test signals

Data moves from memtable to SST and through compaction, so this validates native callback plumbing and CF-specific option persistence into the opened DB. Risks include Java callback lifetime, filter factory ownership, and compaction not being triggered deterministically. Signals are retained value readback and false `keyMayExist` for the filtered empty value.
