# sources/object-store/rustfs/crates/kms/src/encryption/mod.rs

## Purpose
Declares the encryption submodules and re-exports the DEK-facing API for the rest of the KMS crate.

## Important APIs, Types, And Functions
Exports `ciphers` and `dek` modules. Re-exports `AesDekCrypto`, `DataKeyEnvelope`, `DekCrypto`, and `generate_key_material`.

## Control Flow
No runtime control flow; it is a module boundary and public API convenience layer.

## State And Persistence
No state. Persistence types are re-exported from `dek.rs`.

## Dependencies And Integration
Used by KMS backends and services that need DEK wrapping APIs without importing the deeper module path.

## Risks And Edge Cases
`ciphers` is public as a submodule but only DEK items are re-exported. External callers needing object ciphers must import through `encryption::ciphers` if visibility allows from crate boundaries.

## Test Signals
No tests in this file; behavior is covered in `ciphers.rs` and `dek.rs`.
