<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context_impl.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/perf_context_impl.rs

Purpose: captures RocksDB read/write perf counters, reports them to Prometheus and request trackers, and provides instant delta helpers.

Important APIs/types/functions: default perf flag sets, `ReadPerfContext`, `WritePerfContext`, `PerfContextStatistics`, `PerfContextFields`, `PerfStatisticsInstant`, `ReadPerfInstant`, and `WritePerfInstant`.

Control flow: `start` resets RocksDB perf context and applies default flags or explicit level. `report` branches by kind: raftstore write paths observe write latency histograms and tracker fields; storage/coprocessor read paths capture counters, update trackers, accumulate, and periodically flush counters every two seconds.

State and persistence behavior: maintains in-memory accumulated read counters and last flush timestamp. No durable DB state changes.

Dependencies/integration: depends on raw RocksDB perf APIs, Prometheus metrics, TiKV trackers, and `engine_traits::PerfContextKind`.

Risks: uses thread-local RocksDB perf data; cross-thread reporting is invalid. Large metric label lists make drift with RocksDB API possible. `PerfStatisticsInstant` is intentionally `!Send`/`!Sync`.

Test signals: tests validate arithmetic derivations and mutable field access for read perf contexts.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context_impl.rs -->
