# sources/security-integrity/cryfs/crates/crypto/src/hash/backends/sha2.rs

## Purpose
Pure Rust SHA-512 backend using the RustCrypto `sha2` crate.

## Important APIs, types, and functions
- `Sha2Sha512` implements `HashAlgorithmDef` and `HashAlgorithm<64, 8>`.
- Imports `sha2::Digest` trait for `new`, `update`, and `finalize`.

## Control flow
Creates a `sha2::Sha512`, feeds salt then data, finalizes to a generic-array output, converts it into `[u8; 64]`, and returns the shared `Hash` shape.

## State and persistence behavior
No persistent state; returned salt and digest match the common hash format.

## Dependencies and integration points
Provides the portable backend for benchmarks and generic compatibility tests.

## Risks and edge cases
Any change to salt ordering or final byte conversion would break stored hash compatibility. This backend is useful when native OpenSSL/libsodium availability is constrained.

## Test signals
Generic hash tests assert deterministic behavior and exact compatibility vectors for this backend.
