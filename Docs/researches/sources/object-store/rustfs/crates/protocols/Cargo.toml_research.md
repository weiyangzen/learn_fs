# sources/object-store/rustfs/crates/protocols/Cargo.toml

## Purpose

Defines the `rustfs-protocols` crate package metadata, feature flags, runtime dependencies, optional protocol dependencies, dev dependencies, docs.rs metadata, and Linux-specific Tokio io-uring feature.

## Important APIs, Types, and Functions

This is a manifest, not Rust code. Key configuration:

- Package name `rustfs-protocols`, description "Protocol implementations for RustFS (FTPS, SFTP, etc.)".
- Features: empty default, `ftps`, `swift`, `webdav`, and `sftp`.
- Core workspace dependencies include `rustfs-iam`, `rustfs-credentials`, `rustfs-policy`, `rustfs-utils`, `rustfs-config`, `rustfs-storage-api`, and optional `rustfs-tls-runtime`.
- Async/runtime dependencies include `tokio`, `tracing`, `futures-util`, `async-trait`, `time`, and `bytes`.
- S3 DTO dependency is `s3s`.
- Optional protocol stacks pull in libunftp/unftp/rustls, Swift HTTP/crypto/archive dependencies, WebDAV hyper/dav dependencies, and SFTP russh dependencies.
- Dev dependencies include `tempfile`, `proptest`, `tracing-subscriber`, and test-enabled `tokio`.

## Control Flow

Cargo resolves optional dependencies only when corresponding features are enabled. The Linux target section enables Tokio's `io-uring` feature only on Linux.

## State and Persistence

No runtime state. The manifest influences build graph, feature unification, docs.rs builds, and dependency availability.

## Dependencies and Integration Points

This crate bridges protocol implementations with IAM, credentials, policy, config, storage API, and TLS runtime crates. Feature choices determine which protocol modules can compile and what external crates enter the dependency graph.

## Risks and Edge Cases

- Default features are empty, so consumers must opt into protocol features explicitly.
- Feature dependency sets are broad, especially Swift and WebDAV, increasing compile and supply-chain surface when enabled.
- `tokio-util` is optional but configured with feature `rt`; feature interactions should be checked if multiple protocol features require different Tokio-util capabilities.
- docs.rs builds all features, so optional dependencies must remain mutually compatible.

## Test Signals

Manifest-level tests are indirect through crate builds. Dev dependencies indicate property tests and async tests exist elsewhere in the protocols crate. No specific tests are in this file.
