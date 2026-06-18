<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/metrics.rs -->
# sources/storage-engines/tikv/components/external_storage/src/metrics.rs

Purpose: this module defines Prometheus metrics for external-storage creation latency.

Important APIs and constants: `EXT_STORAGE_CREATE_HISTOGRAM` is a `HistogramVec` registered as `tikv_external_storage_create_seconds` with label `type` and exponential buckets from 10 microseconds upward. The crate root's `record_storage_create` observes this histogram with `storage.name()`.

Control flow and state: the metric is lazily registered through `lazy_static!`. Creation timing is recorded by callers after backend construction succeeds.

Dependencies and integration points: it depends on `prometheus` and is used by `export.rs`/`lib.rs`. It emits metrics for local, HDFS, noop, S3, GCS, Azure, or other `ExternalStorage` implementors based on their `name`.

Risks: failed backend creation is not observed because recording occurs after a concrete storage object exists. Label cardinality is low as long as `name()` returns static backend types. Registration unwraps, so duplicate metric names in the process would panic during initialization.

Test signals: no local tests exist; metric registration is checked by crate initialization in tests that call storage creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/metrics.rs -->
