# sources/object-store/rustfs/crates/rio/Cargo.toml

Purpose: this manifest defines the legacy `rustfs-rio` crate, the broader asynchronous I/O framework reused by RustFS and re-exported by rio-v2. It contains the shared reader abstractions, compression/index/checksum/encryption support, and HTTP/S3-adjacent dependencies.

Important dependencies: `tokio` with full features, `futures`, `tokio-util`, `reqwest`, `http`, `s3s`, TLS/runtime crates, metrics, config constants, tracing, `thiserror`, crypto/hash crates (`aes-gcm`, `sha1`, `sha2`, `md-5`, `base64`, `hex-simd`, `faster-hex`), CRC support, and `rustfs-utils` with `io`, `hash`, and `compress` features. Dev dependencies include `tokio-test`, `axum`, and `http-body-util`, suggesting async reader and HTTP integration tests.

State and integration: no runtime state exists in the manifest, but it defines the dependency graph that rio-v2 relies on for traits like `TryGetIndex`, `Index`, and reader wrappers. Feature choices here affect downstream crates that import `rustfs_rio` directly or through rio-v2 re-exports.

Risks and test signals: the crate has a wide dependency surface spanning crypto, compression, HTTP, TLS, and metrics. Workspace-version updates can affect behavior in multiple layers. The manifest itself has no tests; validation comes from compiling downstream crates and running module-level tests such as checksum, compression index, and compression reader tests.
