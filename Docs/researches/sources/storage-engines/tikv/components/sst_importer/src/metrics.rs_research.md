# sources/storage-engines/tikv/components/sst_importer/src/metrics.rs

Purpose: Prometheus metric definitions for SST importer RPCs, upload/write/download/apply/ingest operations, external storage caching, in-memory file cache, and applier engine requests.

Important APIs and metrics: histograms include `IMPORT_RPC_DURATION`, upload chunk bytes/duration, local write chunk duration, download duration/bytes, apply bytes/duration, ingest duration/bytes/count, and applier engine request duration. Counters/gauges include RPC count, local write bytes/keys, importer error counter, apply count, compacted download keys, external storage cache operations, cached file bytes, cache events, and applier events.

Control flow and integration: importer code observes these metrics around gRPC calls, file upload/write paths, external downloads, ingestion, apply, cache operations, and error handling. `errors.rs` increments `IMPORTER_ERROR_VEC`; `cache_map.rs` increments `EXT_STORAGE_CACHE_COUNT`.

State and persistence behavior: process-local Prometheus registry state only.

Risks: metric names include historical typos such as `INPORTER_INGEST_COUNT` and `INPORTER_APPLY_COUNT`; renaming would break dashboards. Label cardinality should remain bounded (`request/result`, `type`, `operation`, `error`).

Test signals: no direct tests; metrics are validated indirectly by compile/link and runtime metric registration.
