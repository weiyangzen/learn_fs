# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/openssl.rs

## Purpose
OpenSSL-backed implementation of the scrypt password-based KDF.

## Important APIs, types, and functions
- `ScryptOpenssl` implements `PasswordBasedKDF`.
- Uses `openssl::pkcs5::scrypt` with `n = 1 << log_n`, `r`, `p`, and `MAXMEM = u64::MAX`.
- Delegates parameter generation to `ScryptParams::generate`.

## Control flow
`derive_key` asserts `log_n < 64`, computes OpenSSL parameters, allocates an `EncryptionKey`, and fills key bytes inside the key initializer closure. OpenSSL errors are converted to panics by `expect`.

## State and persistence behavior
Does not persist state. It consumes serialized/deserialized `ScryptParams` and produces protected-memory key material.

## Dependencies and integration points
Shares `ScryptParams` with the Rust backend, so stored parameter bytes are backend-independent. Used by benchmarks and generic compatibility tests.

## Risks and edge cases
`MAXMEM = u64::MAX` means OpenSSL is not constrained by an application-level memory limit. Invalid parameters or OpenSSL failures panic rather than returning `Result`.

## Test signals
Generic scrypt tests verify reproducibility, exact legacy vectors, empty/unicode/long password behavior, and parity with the default backend.
