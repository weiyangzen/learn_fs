<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/GetBenchmarks.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/GetBenchmarks.java

Purpose: Benchmarks several RocksDB Java `get` paths across different column-family counts, key counts, key sizes, and value sizes.

Important APIs/types/functions: Parameters include `columnFamilyTestType`, `keyCount`, `keySize`, and `valueSize`. Important fields include `DBOptions`, `ReadOptions`, `ColumnFamilyHandle[]`, direct `ByteBuffer` key/value buffers, and reusable byte arrays. Benchmarks are `get`, `preallocatedGet`, and `preallocatedByteBufferGet`.

Control flow: Trial setup loads RocksDB, creates requested column families, writes padded key/value pairs into every CF, flushes, then prepares reusable array and direct-buffer inputs. Each benchmark selects a column family, advances an atomic key index, fills the key representation, and calls a different `RocksDB.get` overload.

State and persistence behavior: The temporary DB is populated and flushed to storage for repeatable reads, then deleted during teardown. The mutable key/value arrays and direct buffers are reused across invocations, making buffer position/reset behavior part of benchmark correctness.

Dependencies and integration points: Depends on RocksDB JNI `open`, `put`, `flush`, and get overloads, JMH, `FileUtils`, `KVUtils.ba`, Java NIO direct buffers, and column-family APIs.

Risks and edge cases: `getColumnFamily` reset logic can briefly return index 0 when wrapping multi-CF tests, skewing distribution. `keyArr` and buffers are benchmark-scoped mutable state, so JMH threading configuration matters. The return value of byte-buffer get is not asserted in benchmark mode.

Test signals: JMH results for the three get modes, no `RocksDBException`, correct value-size assertions when enabled, and cleanup without open-handle errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/GetBenchmarks.java -->
