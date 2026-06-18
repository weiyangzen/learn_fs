# sources/storage-engines/tikv/components/encryption/Cargo.toml

Purpose: This manifest defines the core TiKV encryption crate containing data-key management, master-key backends, file encryption, cloud KMS integration types, metrics, and backup helpers.

Important APIs and settings: Package metadata sets edition 2024 and `publish = false`. Features include `failpoints`, `sm4` via vendored OpenSSL, and `testexport`. Dependencies include `cloud`, `crypto`, `file_system`, `kvproto`, `openssl`, `protobuf`, `prometheus`, `serde`, `tokio`, and TiKV utility crates. A comment explicitly discourages using the general `rand` crate for encryption-related code despite the dependency being present.

Control flow: Cargo uses features to include failpoints and conditional SM4 support. The dependency graph wires the crate to protobuf encryption metadata, cloud KMS providers, OpenSSL ciphers, filesystem abstractions, and metrics.

State and persistence behavior: This file is build metadata only; persistence behavior is implemented in submodules.

Dependencies and integration points: It is consumed by `encryption_export` and TiKV server components that need at-rest encryption and backup encryption support.

Risks: Feature and dependency changes can affect cryptographic compliance, especially SM4/OpenSSL vendoring and RNG selection.

Test signals: Build and crate tests under relevant feature combinations are the main signals.
