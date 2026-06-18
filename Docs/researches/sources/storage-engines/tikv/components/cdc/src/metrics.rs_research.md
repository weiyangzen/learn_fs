# sources/storage-engines/tikv/components/cdc/src/metrics.rs

## Purpose

`metrics.rs` defines Prometheus metrics and helper functions for the CDC component. It covers endpoint task backlog, resolved-ts lag, incremental scan throughput/duration, connection counts, old-value cache and scan details, sink memory, region resolve status, RocksDB perf counters, RawKV outlier lag, event pending duration, and aborted connections.

## Important APIs, Types, And Functions

- `TAG_DELTA_CHANGE` and `TAG_INCREMENTAL_SCAN` label old-value scan metrics by source path: raft delta changes versus incremental scan.
- `make_auto_flush_static_metric!` defines `PerfMetric` labels and `PerfCounter` for RocksDB read perf counters.
- Lazy static metrics include gauges, counters, counter vecs, histogram vecs, and histograms such as:
  - `CDC_ENDPOINT_PENDING_TASKS`
  - `CDC_RESOLVED_TS_GAP_HISTOGRAM`
  - `CDC_SCAN_DURATION_HISTOGRAM`
  - `CDC_SCAN_SINK_DURATION_HISTOGRAM`
  - `CDC_SCAN_BYTES`
  - `CDC_CONNECTION_COUNT`
  - `CDC_DROP_TXN_EXTRA_TASKS_COUNT`
  - `CDC_SCAN_TASKS`
  - `CDC_SCAN_DISK_READ_BYTES`
  - `CDC_MIN_RESOLVED_TS_REGION`, `CDC_MIN_RESOLVED_TS_LAG`, `CDC_MIN_RESOLVED_TS`
  - `CDC_PENDING_BYTES_GAUGE`
  - `CDC_CAPTURED_REGION_COUNT`
  - `CDC_OLD_VALUE_*`
  - `CDC_REGION_RESOLVE_STATUS_GAUGE_VEC`
  - `CDC_RESOLVED_TS_ADVANCE_METHOD`
  - `CDC_GRPC_ACCUMULATE_MESSAGE_BYTES`
  - `CDC_ROCKSDB_PERF_COUNTER` and static wrapper
  - `CDC_RAW_OUTLIER_RESOLVED_TS_GAP`
  - `CDC_EVENTS_PENDING_DURATION`
  - `CDC_ABORTED_CONNECTIONS`
- `TLS_CDC_PERF_STATS` is a thread-local `ReadPerfContext` accumulator.
- `tls_flush_perf_stat!` increments one static RocksDB perf counter.
- `tls_flush_perf_stats` takes and resets the thread-local perf context, then emits every RocksDB perf field.
- `flush_oldvalue_stats` emits TiKV `Statistics` detail counters with CF, tag, and type labels.

## Control Flow

Other CDC files update these metrics inline. `initializer.rs` adds scan bytes, disk-read bytes, durations, scan task counts, old-value stats, and RocksDB perf deltas. `delegate.rs` updates pending lock bytes. `endpoint.rs` updates pending tasks, captured region count, resolve status, min resolved-ts lag, sink bytes/capacity, connection count, dropped transaction-extra tasks, and resolved-ts advancement method.

`TLS_CDC_PERF_STATS` lets scan code accumulate RocksDB perf deltas on the scanning thread, then `tls_flush_perf_stats` drains the local context to global Prometheus counters.

## State And Persistence Behavior

Metrics are process-local runtime state registered with Prometheus. They are not persisted by this file. Lazy registration occurs on first access, and thread-local perf stats are reset after flushing.

## Dependencies And Integration Points

- `prometheus` and `prometheus_static_metric` provide metric registration and static label wrappers.
- `engine_rocks::ReadPerfContext` supplies RocksDB internal read counters.
- `tikv::storage::Statistics` supplies old-value scan detail counters.
- The metric names and labels are part of TiKV observability contracts consumed by dashboards, alerts, and tests.

## Risks And Edge Cases

- Metric registration names are global; duplicate names or label shape changes can break startup or dashboards.
- Gauge/counter semantic mistakes are easy: several old-value cache access/miss values are gauges even though names sound cumulative.
- `tls_flush_perf_stats` must be called from the same thread whose thread-local context was updated; otherwise counters can be delayed or lost until a later flush on that thread.
- Adding RocksDB perf fields requires updating both the static metric enum and flush function in lockstep.
- `flush_oldvalue_stats` depends on stable CF/tag strings from `Statistics::details`.

## Test Signals

There are no direct tests in this file. The metrics are indirectly exercised by delegate, endpoint, and initializer tests that call the paths updating gauges/counters/histograms. Direct metric registration tests would be low value but could catch duplicate name or label cardinality changes.
