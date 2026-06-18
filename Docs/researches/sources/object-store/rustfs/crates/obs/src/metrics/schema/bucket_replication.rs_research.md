# sources/object-store/rustfs/crates/obs/src/metrics/schema/bucket_replication.rs

Purpose: defines descriptor schema and label constants for bucket replication metrics: failures, latency, proxied operations, replicated bytes/count, and bandwidth.

Important APIs/types: label constants `BUCKET_L`, `OPERATION_L`, `TARGET_ARN_L`, and `RANGE_L`; descriptors for last-hour/last-minute failures, total failures, sent bytes/count, proxied GET/HEAD/PUT/tagging/delete-tagging totals/failures, latency, bandwidth limit, and current bandwidth.

Control flow: each descriptor is a `LazyLock<MetricDescriptor>` built with `new_counter_md` or `new_gauge_md`. Most metrics are bucket-labeled; latency includes bucket, operation, range, and target ARN; bandwidth includes bucket and target ARN. Two proxied PUT metric names are constructed via local string constants and `MetricName::from`.

State/persistence: lazy immutable descriptors only.

Dependencies/integration: consumed by `collectors/bucket_replication.rs` and by scheduler tombstone zero metrics. Uses `subsystems::BUCKET_REPLICATION`.

Risks: high-cardinality `target_arn` labels must be stable. Some last-minute/hour failure descriptors are gauges while total failures/sent/proxied operations are counters; callers must respect time-window semantics. Descriptor count is large, increasing maintenance risk when adding new proxied operations.

Test signals: collector tests assert several descriptor-derived metric names and labels, including bandwidth and delete-tagging metrics.
