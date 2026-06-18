# sources/security-integrity/cryfs/crates/crypto/src/kdf/mod.rs

## Purpose
Top-level key-derivation module defining traits for serializable KDF parameters and password-based KDF implementations.

## Important APIs, types, and functions
- `KDFParameters` requires deterministic `serialize` and fallible `deserialize`.
- `PasswordBasedKDF` associates `Settings` and `Parameters`, and provides `derive_key` plus `generate_parameters`.
- Exposes the `scrypt` module.

## Control flow
The traits define contracts only. Concrete implementations generate salt-bearing parameters, derive an `EncryptionKey` of requested size from password bytes and parameters, and allow serialized parameters to reproduce the same key.

## State and persistence behavior
KDF parameters are explicitly intended to be stored with encrypted data. Derived keys are returned as protected-memory `EncryptionKey` values.

## Dependencies and integration points
Connects KDF code to `symmetric::EncryptionKey` and `anyhow::Result`. Filesystem configuration and unlock paths can persist serialized `KDFParameters`.

## Risks and edge cases
Trait methods do not return errors from `derive_key`; current backends panic on invalid parameters or backend errors. That makes deserialize-time validation and compatibility tests important.

## Test signals
Concrete scrypt tests validate parameter serialization and derived key reproducibility across backends.
