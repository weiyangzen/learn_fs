# sources/storage-engines/tikv/components/cloud/src/metrics.rs

## Purpose
Registers shared Prometheus metrics for cloud providers.

## Important APIs, Types, And Functions
- `CLOUD_REQUEST_HISTOGRAM_VEC` records cloud request durations with labels `cloud` and `req`.
- `CLOUD_ERROR_VEC` counts cloud errors with labels `cloud` and `error`.
- `AZBLOB_UPLOAD_DURATION` records Azure Blob upload duration with exponential buckets.

## Control Flow
Metrics are registered lazily via `lazy_static!` and Prometheus `register_*` macros. Provider code observes or increments them around cloud operations and retries.

## State And Persistence Behavior
Metrics live in the process-global Prometheus registry. They are not persisted by this module.

## Dependencies And Integration Points
Used by Azure Blob upload, legacy GCP storage/KMS, GCP v2 storage/KMS, and retry helpers. Depends on `lazy_static` and `prometheus`.

## Risks And Edge Cases
Label values must stay bounded; request labels should remain from controlled operation sets. Registration uses `unwrap()`, so duplicate registration in unusual test/plugin setups can panic. `CLOUD_ERROR_VEC` help text appears stale for a generic cloud metric.

## Test Signals
No direct tests. GCP v2 unit/integration tests assert histogram sample counts for upload and KMS operations.
