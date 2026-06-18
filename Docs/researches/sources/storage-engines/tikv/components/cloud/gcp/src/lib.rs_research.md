# sources/storage-engines/tikv/components/cloud/gcp/src/lib.rs

## Purpose
Defines the legacy GCP provider crate root, re-exporting GCS and KMS implementations and providing small shared request utilities.

## Important APIs, Types, And Functions
- Re-exports `gcs::{Config, GcsStorage}` and `kms::GcpKms`.
- `STORAGE_VENDOR_NAME_GCP` is the canonical `"gcp"` vendor string.
- `utils::retry` wraps `tikv_util::stream::retry_ext`, logs retryable failures, and increments `CLOUD_ERROR_VEC`.
- `utils::read_from_http_body` reads a Hyper body into bytes and converts it into a `tame_gcs::ApiResponse`.

## Control Flow
Provider modules call `utils::retry` around cloud operations. On each failed attempt, the fail hook logs context and increments metrics before retry logic decides whether to continue. `read_from_http_body` is used by list operations to parse typed tame-gcs responses.

## State And Persistence Behavior
This file holds no persistent state. Metrics counters/histograms in the shared `cloud` crate are updated by helper calls.

## Dependencies And Integration Points
Integrates `slog_global` logging, `cloud::metrics`, Hyper body types, `tame_gcs::ApiResponse`, and TiKV retry helpers. Public exports are consumed by provider selection code.

## Risks And Edge Cases
Retry helper metric labels use `"gcp"` and caller-provided operation names, so new operations should keep label cardinality bounded. `read_from_http_body` buffers full response bodies and should not be reused for large object data.

## Test Signals
No direct tests. Indirect coverage comes from GCS/KMS module tests.
