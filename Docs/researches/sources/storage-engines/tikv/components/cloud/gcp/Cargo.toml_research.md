# sources/storage-engines/tikv/components/cloud/gcp/Cargo.toml

## Purpose
Defines the legacy GCP provider crate package and dependency graph. This crate implements GCS and GCP KMS using `tame-gcs`, `tame-oauth`, `hyper`, and hand-written REST/KMS JSON calls.

## Important APIs, Types, And Functions
- Package `gcp`, version `0.0.1`, edition 2021, unpublished Apache-2.0 crate.
- Runtime dependencies include `cloud`, `kvproto`, `tikv_util`, `tame-gcs`, `tame-oauth`, `hyper`, `hyper-tls`, `serde`, `serde_json`, `crc32c`, `regex`, `lazy_static`, and `tokio`.
- `tame-gcs` enables `async-multipart`; dev dependency `matches` supports tests.

## Control Flow
No executable logic lives in the manifest, but dependency choices define runtime behavior: HTTP requests flow through Hyper/TLS and auth through tame OAuth providers.

## State And Persistence Behavior
No state is stored in the manifest.

## Dependencies And Integration Points
The manifest ties the crate into workspace crates `cloud`, `kvproto`, `tikv_util`, and workspace logging crates.

## Risks And Edge Cases
This is the older GCP implementation and differs from `gcp_v2`; dependency upgrades can affect request construction, OAuth support, retry classification, and multipart behavior. `base64 = 0.13` is older than the API style used by newer crates.

## Test Signals
The manifest has no tests; crate tests in `src/gcs.rs` and `src/kms.rs` validate endpoint rewriting, option parsing, key-id parsing, and base64 serialization.
