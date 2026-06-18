# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBBatchOperation.java

Purpose: JUnit coverage for `RDBBatchOperation`, both at the write-batch command assembly layer and against real `DBStore` instances backed by RocksDB.

Important APIs/types/functions: `RDBBatchOperation.newAtomicOperation`, `BatchOperation`, `DBStoreBuilder`, `Table.putWithBatch`, `Table.deleteWithBatch`, `DBStore.commitBatchOperation`, `StringCodec`, `CodecBufferCodec`, and the test-only `TrackingUtilManagedWriteBatchForTesting.Operation`.

Control flow: `testBatchOperation` mocks a column family and verifies that repeated operations on the same key are compacted so only the effective batch writes/deletes are emitted. `testRDBBatchOperationWithRDB` runs 30,000 random puts/deletes into one store through a batch and into a second store directly, commits the batch, then iterates both stores to prove equivalent persisted order and contents.

State and persistence behavior: Real tests create two temporary RocksDB stores and compare persisted key/value streams after commit. The mocked test inspects in-memory write batch state grouped by column family name.

Dependencies and integration points: Integrates with RocksDB native library loading, Ozone configuration, direct and persisted codec-buffer formats, `RocksDatabase.ColumnFamily`, Mockito, and Ratis `CheckedConsumer`.

Risks: Random operation generation can make failures non-reproducible. The large 30,000 operation loop is performance-sensitive. Correctness depends on byte-buffer lifetime and direct-buffer handling during batch deduplication.

Test signals: Strong signal for batch equivalence, direct/persisted codec path parity, and last-write-wins behavior for duplicate keys before commit.
