# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FlushTest.java

## Purpose

Integration test for explicit flush through the Java API.

## Important APIs, control flow, and dependencies

The test opens a DB with create-if-missing and high write-buffer thresholds, writes four keys with `WriteOptions.setDisableWAL(true)`, asserts active memtable entry count is `4`, calls `db.flush(new FlushOptions().setWaitForFlush(true))`, then asserts the active memtable entry count is `0`.

## State, persistence, risks, and test signals

The test moves data from mutable memtable to persisted SST without relying on WAL. Risks include property-name changes, asynchronous flush races if wait is not honored, and write-buffer option interactions. Signals are the `rocksdb.num-entries-active-mem-table` property before and after flush.
