# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ByteBufferUnsupportedOperationTest.java

## Purpose
`ByteBufferUnsupportedOperationTest` is a regression/stress test for a previously intermittent unsupported-operation failure involving Java reverse comparator-backed column families, write batches, and iteration.

## Important APIs and Types
It defines a nested `Handler` that owns a `RocksDB` instance and a concurrent map of `UUID` to `ColumnFamilyHandle`. It uses `Options`, `ColumnFamilyOptions`, `ReverseBytewiseComparator`, `ComparatorOptions`, `ColumnFamilyDescriptor`, `WriteBatch`, `WriteOptions`, and `RocksIterator`.

## Control Flow, State, and Persistence
`Handler` destroys and opens a DB at `testDB`, creates column families with reverse bytewise Java comparator and universal compaction, batches key/value writes into a target CF, and scans values by iterator. `inner` creates 1000 key/value pairs, writes them, and verifies every value is found. The JUnit test repeats `inner` ten times to raise the chance of reproducing intermittent failures, printing the repeat index on runtime exception.

## Dependencies and Integration Points
Depends on JUnit, Rocks native library loading, `TemporaryFolder` though the test currently uses the literal path `testDB`, Java UUID/collections/concurrency utilities, and util `ReverseBytewiseComparator`.

## Risks and Test Signals
The literal DB path can collide with working-directory state and does not use the `TemporaryFolder` rule. `Options` and `ColumnFamilyOptions` are not consistently closed in `Handler`. Despite that, the test is a useful signal for Java comparator, write batch, column family, and iterator interaction under repeated writes.
