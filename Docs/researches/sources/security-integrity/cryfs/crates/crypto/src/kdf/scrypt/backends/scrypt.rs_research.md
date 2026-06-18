# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/scrypt.rs

## Purpose
Default pure Rust scrypt KDF backend using the RustCrypto `scrypt` crate.

## Important APIs, types, and functions
- `ScryptScrypt` implements `PasswordBasedKDF`.
- Builds `scrypt::Params::new(log_n, r, p)`.
- Calls `scrypt::scrypt` to fill an `EncryptionKey`.

## Control flow
`derive_key` converts stored parameters into RustCrypto parameters, panics with parameter debug text on invalid input, then derives into protected key memory. `generate_parameters` delegates to `ScryptParams::generate`.

## State and persistence behavior
No persistent state beyond using persisted `ScryptParams`. Output key is protected and zeroed by `EncryptionKey` semantics.

## Dependencies and integration points
This backend is aliased as `Scrypt` in the parent module and is used by default examples, tests, and benchmark parameter generation.

## Risks and edge cases
A TODO notes some CryFS 1.0 parameter settings may not load in CryFS 2.0 due to RustCrypto parameter constraints. Like OpenSSL, invalid derivation panics instead of returning an error.

## Test signals
Generic scrypt tests cover exact legacy serialized parameters and derived-key vectors, including default settings.
