# sources/storage-engines/tikv/components/encryption/src/metrics.rs

Purpose: Registers Prometheus metrics for encryption metadata and file I/O duration.

Important APIs and types: Lazy static metrics are `ENCRYPTION_DATA_KEY_GAUGE`, `ENCRYPTION_FILE_NUM_GAUGE`, `ENCRYPTION_INITIALIZED_GAUGE`, `ENCRYPT_DECRPTION_FILE_HISTOGRAM`, and `ENCRYPTION_FILE_SIZE_GAUGE`.

Control flow and state: Metrics are globally registered on first access. Gauges are updated by dictionary load/save, file dictionary insert/remove/rewrite, and manager initialization. The histogram is defined for read/write duration labels but this file only registers it.

Dependencies and integration: Depends on `prometheus` macros. Integration points are `file_dict_file.rs`, `manager/mod.rs`, and likely encrypted-file I/O modules outside this work item.

Risks: Metric names and label cardinality are persistent observability contracts. Two descriptions contain spelling errors, but changing names/descriptions may affect dashboards. Registration uses `unwrap`, so duplicate registration would panic if crate initialization were duplicated unexpectedly.

Test signals: No local tests; manager tests check gauge values after initialization and metadata load.
