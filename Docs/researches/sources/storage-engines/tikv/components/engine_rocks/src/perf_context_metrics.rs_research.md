<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context_metrics.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/perf_context_metrics.rs

Purpose: declares Prometheus metrics and static metric label wrappers for RocksDB perf context and SST ingestion timing.

Important APIs/types/functions: `PerfContextType`, `PerfContextTimeDuration`, `CFName`, `IngestType`, `IngestExternalFileTimeDuration`, `From<&str> for CFName`, and lazy static metrics including apply/store histograms, storage/coprocessor counters, ingestion histograms, and allow-write counters.

Control flow: metric macros generate typed label accessors; `CFName::from` normalizes common upper/lower CF names and defaults unknown names to `default`.

State and persistence behavior: owns process-global metric registrations and local auto-flush histogram wrappers. No DB state is persisted.

Dependencies/integration: used by `perf_context_impl.rs` and `import.rs`; depends on `prometheus`, `prometheus_static_metric`, and `lazy_static`.

Risks: unknown CF labels collapse to `default`, which can hide new CFs. Metric registration names and buckets become compatibility surface for monitoring dashboards.

Test signals: no direct tests; metric usage is exercised by perf-context reporting and external-file ingestion paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context_metrics.rs -->
