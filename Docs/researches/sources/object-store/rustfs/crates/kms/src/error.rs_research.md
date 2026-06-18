# sources/object-store/rustfs/crates/kms/src/error.rs

## Purpose
Centralizes KMS error taxonomy and conversions into a crate-wide `Result<T>`.

## Important APIs, Types, And Functions
`KmsError` variants cover configuration, key lookup, invalid keys, cryptographic failure, backend failure, access denied, duplicate key, invalid operation, internal errors, serde, I/O, cache, validation, unsupported algorithms, invalid sizes, and encryption context mismatch. Constructor helpers provide consistent creation. Conversion impls map `std::io::Error`, `serde_json::Error`, `url::ParseError`, and `reqwest::Error`; helper methods map AES-GCM and ChaCha errors.

## Control Flow
There is no complex control flow; errors are built at call sites and propagated with `Result`. Conversions normalize external library failures into KMS-specific categories.

## State And Persistence
No state. Errors derive `Clone`, making them usable in async/test paths that need owned copies, but source error details are stringified rather than retained for most conversions.

## Dependencies And Integration
Uses `thiserror`, crypto crates, `serde_json`, `url`, and `reqwest`. All KMS modules import `KmsError` and `Result`.

## Risks And Edge Cases
Crypto helper conversion messages may be terse because AEAD error types often do not expose details. `invalid_parameter` and `invalid_key_state` both map to `InvalidOperation`, which simplifies API shape but loses specificity. `reqwest::Error` is always categorized as backend error.

## Test Signals
No direct tests in this file, but constructors and variants are exercised throughout config, encryption, manager, and service tests.
