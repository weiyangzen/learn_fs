# sources/object-store/rustfs/crates/kms/Cargo.toml

## Purpose
This manifest defines `rustfs-kms`, the RustFS Key Management Service crate for key generation, storage, backend integration, object encryption, and cryptographic helpers.

## Important APIs, Types, and Functions
The manifest configures package metadata, workspace lint inheritance, crypto dependencies (`aes-gcm`, `chacha20poly1305`, `rand`, `sha2`, `base64`, `zeroize`), async/runtime dependencies (`async-trait`, `tokio`, `uuid`, `jiff`), configuration/serialization/error/logging dependencies, caching via `moka`, and Vault access through `reqwest` and `vaultrs`. Linux targets additionally enable `tokio` `io-uring`.

## Control Flow and Integration Points
The dependency set supports local file backends, Vault KV2, Vault Transit, dynamic API configuration, caching, and object encryption services. Internal RustFS dependencies include `rustfs-utils` and `rustfs-security-governance`.

## State and Persistence Behavior
The manifest itself has no runtime state. It enables backends that persist key material locally or in Vault and a cache layer that stores metadata in memory.

## Dependencies
All versions come from the workspace. Dev dependencies include `tempfile` and `temp-env` for local backend and configuration tests.

## Risks and Edge Cases
The crate includes multiple cryptographic and backend modes in one build with no feature gating beyond an empty default feature set. `tokio` is enabled with `full`, and Linux adds `io-uring`, increasing platform-specific build surface. Vault functionality relies on `vaultrs` and `reqwest`; operational TLS/auth behavior is controlled in configuration source files.

## Test Signals
The manifest does not define explicit integration targets in this subset. Unit tests in backend, cache, and API modules are discovered normally.
