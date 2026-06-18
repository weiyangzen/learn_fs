# sources/storage-engines/tikv/components/tikv_kv/src/stats.rs

Purpose: collects scan, iterator, tombstone, block-read, flow, and latency statistics for KV reads and GC metrics across default, lock, and write column families.

Important APIs: `StatsCollector` snapshots an `IterMetricsCollector` before an iterator operation and updates a mutable `CfStatistics` on drop. `CfStatistics` stores operation counts, processed keys, tombstone counters, raw-value tombstones, flow stats, and missing-range counters. `Statistics` aggregates per-CF stats plus processed size and load-data hints. `LoadDataHint` switches between near-seek and seek based on write-CF over-seek-bound changes. `StatisticsSummary` accumulates multiple `Statistics`; `StageLatencyStats` stores read-stage latency indicators.

Control flow: callers create `StatsCollector::new()` around next/prev/seek/seek-for-prev calls. Its `Drop` computes deltas for raw tombstone TLS, block reads, and internal delete skipped count, then increments the operation-specific counters. `Statistics::load_data_hint()` compares current and last write-CF over-seek-bound to choose a data loading strategy.

State and persistence: all stats are in-memory request/query counters. `RAW_VALUE_TOMBSTONE` is thread-local and sampled by collectors. Saturating addition prevents counter overflow in per-CF aggregation.

Dependencies and integration: uses `engine_traits::IterMetricsCollector`, raftstore `FlowStatistics`, protobuf `ScanDetail`/`ScanDetailV2`, and metric enums from `metrics.rs`. `details_enum()` provides structured labels for GC metric emission.

Risks: `mut_cf_statistics()` and `cf_statistics()` panic on unknown CF names; raw tombstone accounting depends on TLS discipline; `Statistics::add()` uses normal addition for `processed_size`, unlike saturating per-CF fields. Deprecated protobuf conversion methods still exist for compatibility.

Test signals: no local tests here, but `lib.rs` shared tests assert cursor statistics behavior; metric-label alignment is indirectly compile-checked through enum usage.
