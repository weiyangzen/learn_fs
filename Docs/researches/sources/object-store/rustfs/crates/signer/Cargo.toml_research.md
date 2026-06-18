# sources/object-store/rustfs/crates/signer/Cargo.toml

## Purpose
Defines the `rustfs-signer` crate for AWS/S3-style request signing and presigning. The manifest identifies cryptography, web programming, and MinIO compatibility as the package domain.

## Dependencies and Integration
Dependencies include `http`, `hyper`, `s3s::Body`, `time`, `bytes`, `serde_urlencoded`, `base64-simd`, `tracing`, `thiserror`, and `rustfs-utils` with crypto/hash helpers. Doctests are disabled and workspace lints apply.

## Risks and Test Signals
The crate depends on canonicalization-sensitive libraries (`http::Uri`, `HeaderValue`, URL encoding) and project crypto wrappers. Build risk is moderate because signing behavior must remain compatible with AWS and S3-compatible services. Unit tests live in the signer modules.
