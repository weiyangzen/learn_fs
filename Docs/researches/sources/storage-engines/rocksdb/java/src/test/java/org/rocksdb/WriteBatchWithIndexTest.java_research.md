# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteBatchWithIndexTest.java

Purpose: JUnit coverage for RocksJava `WriteBatchWithIndex`, especially read-your-own-writes semantics, batch index iteration, column family overloads, savepoints, direct/heap `ByteBuffer` APIs, and lookup helpers.

Important APIs/types/functions: `WriteBatchWithIndex`, `WBWIRocksIterator`, `RocksIterator`, `ReadOptions`, `WriteOptions`, `ColumnFamilyHandle`, `DirectSlice`, `ByteBufferAllocator`, `getFromBatch`, `getFromBatchAndDB`, `newIteratorWithBase`, `setSavePoint`, `rollbackToSavePoint`, `popSavePoint`, `setMaxBytes`, `getWriteBatch`.

Control flow and state: tests open temporary RocksDB instances, populate base DB state, then layer a `WriteBatchWithIndex` over base iterators. The merged iterator is probed with `seek`, `seekForPrev`, forward iteration, and reverse iteration after puts, deletes, single deletes, and reinserts. Column family tests repeat the same state transitions through explicit CF handles. Savepoint tests mutate keys after nested savepoints, then roll back or pop and assert the visible batch view. `iterator()` builds expected `WriteEntry` objects and verifies seek/iteration behavior for array-backed and direct buffers. `getFromBatchAndDB` checks batch values shadow DB values and deletes hide DB data.

State and persistence behavior: batch mutations are in-memory until `db.write()` persists them. Base DB values remain durable across iterator construction, while the indexed batch overlays newer, deleted, or missing keys. `getWriteBatch()` returns a non-owning native wrapper, so lifetime is tied to the parent batch-with-index.

Dependencies and integration points: integrates RocksJava JNI, native library loading through `RocksNativeLibraryResource`, JUnit `TemporaryFolder`, AssertJ, column family open APIs, `ByteBuffer` direct and heap paths, and helper `ByteBufferAllocator`.

Risks: iterator validity is easy to misuse after deletes because nearest-key behavior must be checked against the requested key. The tests expose native-handle lifetimes and non-owning write batch handles. Direct `ByteBuffer` methods consume buffer positions, so callers must flip/reset as expected. Savepoint stack underflow intentionally throws `RocksDBException`.

Test signals: strong coverage for default and named CFs, direct/heap buffer seeking, overwrite true/false iterator constructors, max-batch-size enforcement, exact-match lookup, range delete half-open boundaries, and savepoint exception paths.
