<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/ComparatorBenchmarks.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/ComparatorBenchmarks.java

Purpose: Benchmarks RocksDB put performance under native and Java comparator implementations, including direct/non-direct buffer and reused-buffer synchronization modes for Java comparators.

Important APIs/types/functions: JMH annotations `@State`, `@Param`, `@Setup`, `@TearDown`, and `@Benchmark`; RocksDB `Options`, `BuiltinComparator`, `ComparatorOptions`, `AbstractComparator`, `BytewiseComparator`, `ReverseBytewiseComparator`; `Counter` state; and `put`.

Control flow: Trial setup loads RocksDB, creates a temporary DB directory, builds options, parses `comparatorName` to choose native bytewise/reverse comparators or construct Java comparator options, opens the DB, and the benchmark repeatedly puts incrementing key/value pairs. Tear down closes DB/comparator/options and recursively deletes the directory.

State and persistence behavior: Each trial creates a real temporary RocksDB instance and persists benchmark writes until teardown deletes it. `Counter` is benchmark-scoped and atomically generates unique integer suffixes.

Dependencies and integration points: Depends on JMH, RocksDB JNI comparator APIs, `FileUtils.delete`, and `KVUtils.ba`. It exercises JNI callback comparator overhead and buffer reuse modes.

Risks and edge cases: Comparator-name parsing is string-fragment based, so ambiguous substrings could select unintended options. Writes grow the DB for the trial duration and can include compaction effects. Temporary cleanup relies on all native handles closing first.

Test signals: JMH throughput/latency by `comparatorName`, absence of cleanup failures, and successful runs across all Java comparator synchronization modes indicate coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/jmh/ComparatorBenchmarks.java -->
