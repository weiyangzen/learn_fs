# sources/storage-engines/tikv/components/tidb_query_common/src/metrics.rs

Purpose: defines coprocessor executor metrics and tracker updates for pushed-down query execution.

Important APIs and control flow: `make_auto_flush_static_metric!` declares `ExecutorName` labels and a local counter type. `COPR_EXECUTOR_COUNT` registers `tikv_coprocessor_executor_count`; `EXECUTOR_COUNT_METRICS` exposes an auto-flushing local metric. `record_executor_work` skips zero work, asserts supported batch executor labels in debug builds, and saturating-adds work counts into the TLS tracker. `record_coprocessor_executor_iterations` similarly records iteration counts.

State and persistence behavior: metrics are held in Prometheus counters and thread-local tracker fields, not durable storage. Saturating additions prevent overflow panics.

Dependencies and integration: depends on `prometheus`, `prometheus_static_metric`, and `tracker::with_tls_tracker`. Executors call these hooks to update observability data.

Risks and test signals: `record_executor_work` only maps a subset of labels; unsupported labels no-op outside debug assertions. Metric registration unwraps at initialization, so duplicate registration or registry failures panic. Coverage is usually integration/metrics based.
