# sources/storage-engines/tikv/components/cloud/src/lib.rs

## Purpose
Defines the shared `cloud` crate root for TiKV cloud provider integration. It exposes error, KMS, blob, and metrics modules plus common vendor constants.

## Important APIs, Types, And Functions
- Enables nightly features `test` and `min_specialization`.
- Re-exports `Error`, `ErrorTrait`, `Result`, KMS config/key/provider types, and blob `BucketConf`/`StringNonEmpty` helpers.
- Defines `STORAGE_VENDOR_NAME_GCP` and `STORAGE_VENDOR_NAME_GCP_V2`.
- Public modules are `error`, `kms`, `blob`, and `metrics`.

## Control Flow
There is no runtime control flow. The file defines the crate's public API surface.

## State And Persistence Behavior
No state is stored here. Metrics are registered in `metrics.rs` when referenced through lazy statics.

## Dependencies And Integration Points
All provider crates depend on this crate for shared contracts. Downstream TiKV backup/encryption code imports these re-exports to avoid provider-specific dependencies.

## Risks And Edge Cases
Public re-export choices are API commitments inside the workspace. Vendor constants only include GCP/GCP v2 here; Azure has its own crate-level constant.

## Test Signals
No direct tests. Compile coverage of re-exports occurs through provider crates.
