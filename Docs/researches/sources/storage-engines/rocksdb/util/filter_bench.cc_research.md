# sources/storage-engines/rocksdb/util/filter_bench.cc

Purpose: gflags-driven benchmark and validation tool for RocksDB Bloom-like filter implementations, full-filter readers, and plain-table Bloom filters.

Important types/functions: `KeyMaker` generates varied keys with optional alignment/size variation. `FilterInfo` stores built filter data/readers and FP counters. `FilterBench` extends `MockBlockBasedTableTester`; `Go()` builds filters, verifies no false negatives and acceptable FP rate, then runs query workloads. `RandomQueryTest()` measures gross/dry-run query time for single, batched, random, and skewed filter selection modes.

Control flow: if gflags is unavailable, executable returns an error. Flags choose implementation, memory/key limits, bits per key, batch size, reader interface, cache charging, quick/best-case modes, and runs. Build phase repeatedly creates filters until memory/key target. Verification checks inside keys and outside FP rate. Query phase compares real filter time to dry-run hashing/testing overhead.

State and persistence: benchmark-only in-memory state: arenas, filter buffers, readers, random seed, FP reports, optional block cache. No persistence.

Dependencies and integration: includes table filter internals, mock block table tester, plain-table Bloom, cache, arena, hash/fastrange, random, stopwatch, gflags compatibility, and stderr logger.

Risks: benchmark results are sensitive to compiler optimization, assertions, CPU cache, malloc usable size, and flag combinations. Some flag combinations throw runtime errors. FP assertions are probabilistic unless `allow_bad_fp_rate` is set.

Test signals: not a unit test by default but useful performance/FP-rate signal for filter implementation changes.
