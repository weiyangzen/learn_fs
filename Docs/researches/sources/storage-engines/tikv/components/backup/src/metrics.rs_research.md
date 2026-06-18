# sources/storage-engines/tikv/components/backup/src/metrics.rs

## Purpose
This module registers Prometheus metrics used by the backup component to observe backup range latency, output sizes, worker pool sizing, errors, soft limits, scanner backpressure, scanned KV counts/sizes, and raw KV TTL expiration.

## Important APIs, Types, And Functions
The file uses `lazy_static!` to define `BACKUP_RANGE_HISTOGRAM_VEC`, `BACKUP_RANGE_SIZE_HISTOGRAM_VEC`, `BACKUP_THREAD_POOL_SIZE_GAUGE`, `BACKUP_RANGE_ERROR_VEC`, `BACKUP_SOFTLIMIT_GAUGE`, `BACKUP_SCAN_WAIT_FOR_WRITER_HISTOGRAM`, `BACKUP_SCAN_KV_COUNT`, `BACKUP_SCAN_KV_SIZE`, and `BACKUP_RAW_EXPIRED_COUNT`.

## Control Flow
Metric registration occurs lazily on first access through Prometheus registration macros. Histograms use exponential buckets for range duration and range size. Counters/gauges are mutated by endpoint scanning, error conversion, writer behavior, and soft-limit updates.

## State And Persistence Behavior
The module maintains process-global metric collectors registered in Prometheus’s default registry. It does not persist data to disk; metric state lives in process memory and is scraped/exported by TiKV’s metrics subsystem.

## Dependencies And Integration Points
It depends on `prometheus` and `lazy_static`. Endpoint code observes snapshot/scan/raw-scan durations, thread pool size, soft-limit cap, scanner wait time, and raw expired count. `errors.rs` increments `BACKUP_RANGE_ERROR_VEC`. Writer/scanner modules likely update size/count histograms and counters.

## Risks And Edge Cases
Prometheus registration uses `.unwrap()`, so duplicate metric names in the same process would panic at first access. Label cardinality is intentionally small (`type`, `cf`, `error`), and callers should preserve that. A comment reminds maintainers to update Grafana dashboards when metrics change.

## Test Signals
There are no inline tests. Metrics are indirectly exercised by endpoint tests that update gauges/counters/histograms during backup, error, and raw TTL scenarios.
