# sources/storage-engines/foundationdb/fdbclient/bench/BenchMetadataCheck.cpp

Purpose: compares two methods for detecting whether clear-range mutations touch metadata/system keyspace in `applyMetadataMutations`-style code.

Important APIs and control flow: a static array defines five `ClearRange` mutations covering normal keys, short user ranges, long user ranges, normal-to-system overlap, and system-prefixed ranges. `bench_check_metadata1` uses `KeyRangeRef(m.param1, m.param2).intersects(systemKeys)`. `bench_check_metadata2` performs a cheaper byte check on `param2`.

State and persistence: no persistent state; it benchmarks CPU-only predicate costs.

Dependencies and integration: uses `CommitTransaction.h`, `FDBTypes.h`, `SystemData.h`, and Google Benchmark. Its results inform metadata mutation filtering in commit/restore paths.

Risks: the byte-check benchmark is intentionally narrower than full range intersection and may not encode all semantic cases. Any optimization based on it must preserve correctness for boundary and empty-range behavior.

Test signals: both benchmarks run over all mutation cases using `DenseRange` and aggregate reporting.
