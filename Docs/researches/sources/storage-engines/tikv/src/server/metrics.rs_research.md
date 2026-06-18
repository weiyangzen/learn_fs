# sources/storage-engines/tikv/src/server/metrics.rs

Purpose: central server metrics module declaring Prometheus counters, gauges, histograms, static label enums, and local auto-flush handles for gRPC, GC, snapshot, raft transport, config, async storage, resource priority, and request-source metrics.

Important APIs/types/functions: static metric enums include `GrpcTypeKind`, `GcCommandKind`, `SnapTask`, `ResolveStore`, `ResourcePriority`, raft duration/flush labels, request status/type labels, and `From<ErrorHeaderKind>`/`From<u64>` mappings. Runtime helper `record_request_source_metrics` keeps thread-local per-source counters and flushes periodically.

Control flow: most code lazily registers metrics and exports static handles. `record_request_source_metrics` checks a thread-local last-flush timestamp, lazily creates local counters per source string, increments count and duration, and flushes once per second. Error header conversion maps storage response error categories to async request metric labels.

State and persistence: state is process metrics registry plus thread-local metric maps. No durable state exists.

Dependencies and integration: used by many server modules including raft client, proxy, GC worker, raftstore-facing services, and config reporting. Re-exports GC key metric types from storage KV metrics.

Risks: high-cardinality `source` values in `record_request_source_metrics` can grow thread-local maps and Prometheus label series. Registration unwraps can panic on duplicate metric names. Static label enums require coordinated updates with call sites.

Test signals: no local unit tests; metrics are indirectly exercised by components that use the exported statics.
