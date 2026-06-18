# sources/storage-engines/tikv/components/cloud/gcp_v2/Cargo.toml

## Purpose
Defines the newer GCP provider crate using generated Google Cloud Rust clients for Storage and KMS, with optional FIPS crypto-provider support.

## Important APIs, Types, And Functions
- Package `gcp_v2`, version `0.0.1`, edition 2021, unpublished Apache-2.0 crate.
- Feature `fips = ["rustls/fips"]` toggles FIPS provider installation.
- Runtime dependencies include `google-cloud-storage`, `google-cloud-gax`, `google-cloud-auth`, `google-cloud-kms-v1`, `rustls`, `tokio`, `futures`, `async-stream`, `bytes`, `crc32c`, `cloud`, `kvproto`, and `tikv_util`.
- Dev dependencies include `prometheus` and `tempfile`.

## Control Flow
No runtime logic lives here, but dependency choices drive async generated clients, rustls provider setup, generated KMS/storage builders, and external-account/service-account credential support.

## State And Persistence Behavior
No manifest state beyond Cargo metadata.

## Dependencies And Integration Points
This crate coexists with legacy `gcp`; shared storage/KMS contracts come from `cloud`, and kvproto input still uses `brpb::Gcs`.

## Risks And Edge Cases
Google client versions and rustls feature flags are critical integration points. FIPS behavior depends on process-global rustls crypto-provider initialization. `anyhow` appears present but not central in reviewed source.

## Test Signals
Integration tests in `tests/metrics.rs` depend on Tokio, tempfile, and generated clients. Unit tests in `src/lib.rs`, `src/kms.rs`, and `src/credentials.rs` validate credential mode, metrics, and KMS stubs.
