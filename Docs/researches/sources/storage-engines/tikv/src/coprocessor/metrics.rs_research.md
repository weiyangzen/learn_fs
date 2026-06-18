# sources/storage-engines/tikv/src/coprocessor/metrics.rs

Purpose: defines Prometheus metrics, static label enums, TLS-local aggregation, PD read-flow reporting, and memory-quota gauges for coprocessor.

Important APIs/types: label enums include request tags, CFs, scan kinds, wait types, memory-lock check results, analyze metric kinds, and semaphore acquisition types. Registered metrics cover request duration/handle/wait/handler-build, request errors, scan keys/details, DAG count, response bytes, semaphore waits, memory-lock checks, analyze I/O counters/ratio, and memory quota. `CopLocalMetrics` stores TLS scan details and `ReadStats`. `tls_flush` emits Prometheus counters and PD read stats through a `FlowStatsReporter`. `tls_collect_scan_details`, `tls_collect_read_flow`, and `tls_collect_query` aggregate per-thread data. `register_coprocessor_memory_quota_metrics` registers a custom collector exposing capacity and in-use bytes.

State and persistence: all state is in process-local Prometheus registries and thread-local buffers; PD read stats are flushed by read-pool tickers. No durable writes occur. Dependencies include `prometheus`, `prometheus_static_metric`, raftstore read stats, PD bucket metadata, server GC metric enums, and `MemoryQuota`.

Integration points: endpoint/tracker collect stats, readpool tickers call `tls_flush`, analyze code increments analyze metrics, and concurrency/deadline paths update semaphore/deadline-related metrics. Risks include high cardinality if labels expand, TLS metrics not flushing on idle/stopped threads, duplicate memory-quota collector registration warnings, and stale PD flow if tickers fail. Test-only helpers expose and clear local read stats.
