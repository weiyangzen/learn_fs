<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/PutBenchmarks.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/PutBenchmarks.java

Purpose: Benchmarks Java put paths for byte arrays and direct `ByteBuffer`s across different column-family counts, key counts, key sizes, and value sizes.

Important APIs/types/functions: Parameters include `columnFamilyTestType`, `keyCount`, `keySize`, `valueSize`, and `bufferListSize`. Key methods are `setup`, `cleanup`, `getColumnFamily`, `borrow`, `repay`, `put`, `putByteArrays`, and `putByteBuffers`; `Counter` produces unique key suffixes.

Control flow: Setup creates a temporary DB with requested column families and preallocates pools of byte-array and direct-buffer key/value storage. Each benchmark borrows buffers, writes `keyN`/`valueN` prefixes into padded storage, calls a RocksDB `put` overload, and returns buffers to the pool.

State and persistence behavior: Benchmark writes persist in the temporary RocksDB directory until teardown. Buffer pools are benchmark-scoped mutable lists guarded by `synchronized`; direct buffers are reused after `clear`/`flip`.

Dependencies and integration points: Depends on RocksDB JNI `put` overloads, `WriteOptions`, JMH state, `FileUtils`, and `KVUtils.ba`. It exercises JNI marshalling and column-family handle paths.

Risks and edge cases: `putByteArrays` and `putByteBuffers` create new `WriteOptions` per operation and never close them, which can distort benchmarks and leak native resources. Borrow sleeps for one second if pools are empty, affecting high-concurrency results. CF wrap logic can return default CF unexpectedly.

Test signals: JMH output by put mode and parameter set, absence of native resource warnings, and cleanup success. Profiling should highlight allocation impact from per-operation `WriteOptions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/PutBenchmarks.java -->
