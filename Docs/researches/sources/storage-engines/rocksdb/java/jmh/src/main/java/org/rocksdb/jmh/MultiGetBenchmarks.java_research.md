<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/MultiGetBenchmarks.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/MultiGetBenchmarks.java

Purpose: Benchmarks Java multi-get APIs using byte-array key lists, explicit column-family handle lists, random column-family handle lists, and direct `ByteBuffer` result buffers.

Important APIs/types/functions: Parameters include `columnFamilyTestType`, `keyCount`, `multiGetSize`, `valueSize`, and `keySize`. Key methods are `setup`, `cleanup`, `next`, `allocateSliceBuffers`, `multiGetList10`, `multiGetListExplicitCF20`, `multiGetListRandomCF30`, `multiGetBB200`, and `main`.

Control flow: Trial setup creates the DB and optional column families, writes padded values for keys, builds repeated/default/random CF-handle lists, and flushes. Per-invocation setup allocates direct buffers and slices. Each benchmark reserves a key range atomically, builds key lists or buffer slices, calls a `multiGet` variant, and validates returned status/value lengths.

State and persistence behavior: The trial DB contains flushed benchmark data until teardown. `keysBuffer`/`valuesBuffer` and slice lists are per-thread state. `keyIndex` advances through key ranges and wraps by multi-get size.

Dependencies and integration points: Depends on RocksDB JNI multi-get APIs, `ByteBufferGetStatus`, JMH, `KVUtils.keys`, `FileUtils.delete`, and column-family handles. It directly tests high-throughput JNI marshalling paths.

Risks and edge cases: When `cfs` is zero, building `randomCFHandles` with `Math.random() * cfs` would always select index 0 only because the loop still runs; with zero optional CFs that is the default handle from the descriptor list, so behavior is not random but valid. The `main` uses parameter names with trailing `=`, which may not match intended JMH API usage. Direct buffer allocation size can be very large.

Test signals: JMH results plus the explicit status/value-size runtime checks in benchmarks. Failures show as `RuntimeException` for wrong status/size or native exceptions for API misuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/MultiGetBenchmarks.java -->
