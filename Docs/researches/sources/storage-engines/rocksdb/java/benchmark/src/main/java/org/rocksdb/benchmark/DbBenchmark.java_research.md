<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/benchmark/src/main/java/org/rocksdb/benchmark/DbBenchmark.java -->
# Research: sources/storage-engines/rocksdb/java/benchmark/src/main/java/org/rocksdb/benchmark/DbBenchmark.java

Purpose: Implements a standalone Java benchmark driver for RocksDB JNI, modeled after `db_bench` workloads. It opens a configurable DB, runs write/read workloads, and prints throughput/latency summaries.

Important APIs/types/functions: `Stats` records per-task timing, counts, bytes, found keys, and reporting. `DbBenchmark` defines `BenchmarkTask`, `WriteTask`, `WriteSequentialTask`, `WriteRandomTask`, `WriteUniqueRandomTask`, `ReadRandomTask`, `ReadSequentialTask`, `RandomGenerator`, and the large `Flag` enum. Key methods include `prepareOptions`, `prepareReadOptions`, `prepareWriteOptions`, `run`, `open`, `stop`, `generateKeyFromLong`, `main`, and `Flag.parseValue`.

Control flow: `main` seeds defaults from `Flag`, parses `--flag=value` arguments, constructs `DbBenchmark`, and calls `run`. `run` optionally destroys the DB, prepares options, opens RocksDB, loops through requested benchmark names, builds foreground/background `Callable<Stats>` tasks, invokes them through executors, stops background work, and reports aggregate stats. Write tasks generate sequential/random/unique-random keys and optionally batch writes; read tasks use `get` or iterator scans.

State and persistence behavior: The benchmark writes to a RocksDB path from `--db`, using configurable WAL, sync, memtable, cache, compaction, mmap, and env settings. `destroyDb` currently closes the DB but does not delete files, so "fresh" behavior is incomplete. `RandomGenerator` reuses a compressible byte buffer for value generation.

Dependencies and integration points: Depends on RocksDB Java API classes, memtable/table config classes, `RocksMemEnv`, `SizeUnit`, Java reflection for custom comparators, Java executors, and `jdb_bench.sh`. It exercises many JNI option setters and `RocksDB.put/get/write/newIterator`.

Risks and edge cases: `destroyDb` is a TODO and can leave stale data. `getTempDir` uses `File.pathSeparator` when falling back, likely producing a bad path separator for directory construction. Some flags are parsed but not implemented. `WriteOptions` objects are shared across concurrent tasks; correctness depends on native wrapper thread-safety for const use. Batches are manually disposed inside loops.

Test signals: Running `make db_bench` then `java ... DbBenchmark --benchmarks=...` should report ops/sec and MB/s. Useful checks include comparing found counts, ensuring no unknown benchmark names, validating custom comparator construction, and confirming temporary DB cleanup expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/benchmark/src/main/java/org/rocksdb/benchmark/DbBenchmark.java -->
