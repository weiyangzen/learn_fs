# sources/storage-engines/rocksdb/util/dynamic_bloom_test.cc

Purpose: GoogleTest/gflags-based validation and optional performance testing for `DynamicBloom`.

Important tests: `EmptyFilter`, `Small`, and `SmallConcurrentAdd` validate basic membership behavior. `VaryingLengths` inserts up to hundreds of thousands or perf-mode tens of millions of sequential/non-sequential keys and checks false positive rates. `perf` measures add/query latency when enabled. `concurrent_with_perf` uses four threads for concurrent adds, hits, and miss/false-positive measurement.

Control flow: if `GFLAGS` is unavailable, the executable prints a skip message and returns success. With gflags, command-line flags control bits per key, probes, and perf scale. `KeyMaker` creates sequential and non-sequential key slices backed by object fields.

State and persistence: tests use arena-backed in-memory filters and local counters/timers; no persistence.

Dependencies and integration: includes `dynamic_bloom.h`, arena, port threads, system clock, gflags compatibility, test harness, and stopwatch utilities.

Risks: probabilistic false-positive checks can be sensitive to hash/filter changes. Perf mode can allocate/process very large filters. Sequential-key cases can hide 32-bit hash weaknesses, which comments explicitly note.

Test signals: strong direct signal for DynamicBloom correctness and approximate FP-rate expectations, conditional on gflags availability.
