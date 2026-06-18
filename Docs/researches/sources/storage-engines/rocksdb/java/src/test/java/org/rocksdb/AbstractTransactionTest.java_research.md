# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/AbstractTransactionTest.java

## Purpose
`AbstractTransactionTest` is a shared JUnit base for regular and optimistic transaction tests. It defines common behavioral expectations for transaction snapshots, commit/rollback, reads/writes, column families, buffers, merge, untracked operations, indexing, write options, and batch rebuilding.

## Important APIs and Types
The abstract `startDb()` returns a `DBContainer`, which supplies `beginTransaction()` overloads and access to a test column family. Tests cover `Transaction`, `ReadOptions`, `WriteOptions`, `WriteBatch`, `WriteBatchWithIndex`, `Snapshot`, `GetStatus`, and `ColumnFamilyHandle`. `TestTransactionNotifier` records snapshots from `setSnapshotOnNextOperation`.

## Control Flow, State, and Persistence
Each test creates a temporary DB container and uses try-with-resources to close DBs, options, and transactions. Commit tests verify persisted visibility after transaction close; rollback/savepoint tests verify staged writes are removed. Byte-array and `ByteBuffer` tests inspect target-buffer positions, required sizes, and partial reads. Merge tests rely on configured merge operators with different default/CF delimiters. Untracked operations are committed and reopened to validate persistence. `rebuildFromWriteBatch` imports a separate batch into a transaction.

## Dependencies and Integration Points
Depends on JUnit, AssertJ, `TemporaryFolder`, `PlatformRandomHelper`, UTF-8 utilities, and the RocksDB Java transaction API. Concrete subclasses provide DB setup and merge/operator configuration.

## Risks and Test Signals
This file is a major test signal for transaction API stability. It catches handle ownership (`getSnapshot`, `getWriteBatch`, `getWriteOptions`, commit-time batch), buffer handling, column-family overload symmetry, savepoints, lock timeout, log number state, and merge behavior. Some helper methods for heap `ByteBuffer` merge lack `@Test`, so subclasses or future changes should confirm intended coverage.
