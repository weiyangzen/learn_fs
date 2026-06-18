# sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket_replication.rs

Purpose: converts per-bucket replication and per-target bandwidth snapshots into `PrometheusMetric` values using descriptors from `schema::bucket_replication`. It covers failure bytes/counts, sent bytes/counts, proxied request totals/failures, replication latency, and bandwidth limit/current EWMA.

Important APIs/types: `BucketReplicationTargetStats`, `BucketReplicationBandwidthStats`, `BucketReplicationStats`, `collect_bucket_replication_bandwidth_metrics`, and `collect_bucket_replication_metrics`. The main stats struct is a decoupled DTO with bucket identity, counters/gauges for replication failures and proxied operations, and a `targets` vector for target-specific latency.

Control flow: bandwidth collection returns early for empty input, then emits two metrics per `(bucket,target_arn)`. bucket replication collection returns early for empty input, preallocates `20 + targets.len()` per bucket, emits fixed bucket-labeled metrics, then emits one latency metric per target with labels `bucket`, `operation=object_replication`, `range=all`, and `target_arn`.

State/persistence: pure in-memory conversion; no local persistence. The lifecycle of stale bandwidth series is handled in `scheduler.rs` tombstone logic, not here.

Dependencies/integration: depends on `PrometheusMetric` and bucket replication schema constants/descriptors. Called by the metrics runtime's bucket replication bandwidth task after `stats_collector` snapshots are collected.

Risks: high cardinality from `bucket` and `target_arn`; latency target stats include unused bandwidth fields, so callers must also feed `collect_bucket_replication_bandwidth_metrics` for bandwidth series. The capacity estimate uses `BASE_BUCKET_REPLICATION_METRICS_PER_BUCKET + targets.len()`, matching current latency-only target expansion.

Test signals: unit tests cover non-empty and empty replication detail output, label assertions for bucket and target ARN, proxied PUT and delete tagging metrics, and bandwidth limit/current metrics.
