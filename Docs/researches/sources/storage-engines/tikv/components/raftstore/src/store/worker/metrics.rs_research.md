# sources/storage-engines/tikv/components/raftstore/src/store/worker/metrics.rs

## Purpose
This file defines Prometheus metrics for raftstore workers and local-read paths. It centralizes counters, gauges, histograms, static label enums, and thread-local local-read metric buffering.

## Important APIs, Types, and Functions
- Static metric label enums and wrappers: `SnapType`, `SnapStatus`, `SnapCounter`, `CheckSplitCounter`, `SnapHistogram`, `RejectReason`, `LocalReadRejectCounter`, `ClearOverlapRegionType`, and `ClearOverlapRegionDuration`.
- `LocalReadMetrics` groups per-thread local counters and last flush time.
- `TLS_LOCAL_READ_METRICS` initializes thread-local local metric handles.
- `maybe_tls_local_read_metrics_flush` flushes thread-local counters every 10 seconds.
- Lazy Prometheus collectors include snapshot counters/histograms, split-check metrics, compaction metrics, process CPU gauge, hash metrics, stale-peer cleanup gauge, raft-log GC metrics, local-read counters/reject reasons, and clear-overlap-region duration.

## Control Flow
Metrics are registered lazily with `lazy_static!`. Callers increment local or global collectors directly. For local reads, worker threads update thread-local counters to reduce contention; `maybe_tls_local_read_metrics_flush` checks elapsed coarse time and flushes all local counters and reject-reason vectors when the interval has passed.

## State and Persistence Behavior
All state is in process memory and exported through Prometheus. Thread-local counters buffer increments until flush. There is no disk persistence. Metric names and labels form an external observability contract and should be treated as stable.

## Dependencies and Integration Points
The file depends on `prometheus`, `prometheus_static_metric`, `lazy_static`, and `tikv_util::time::Instant`. It is imported by compaction, consistency check, snapshot, split, local read, raft log GC, and cleanup paths.

## Risks and Edge Cases
Metric label enums must stay synchronized with call sites; invalid label values would fail at compile time for static metrics but dynamic vectors still require care. Thread-local metrics depend on periodic flush calls; low-traffic threads may retain increments longer than expected. The name `CHECK_SPILT_*` preserves an existing typo in the metric variable names while metric strings use check-split wording.

## Test Signals
There are no direct tests in this file. Runtime validation comes from compilation of static metric labels, Prometheus registration success at startup, and call-site tests that observe worker behavior while incrementing metrics.
