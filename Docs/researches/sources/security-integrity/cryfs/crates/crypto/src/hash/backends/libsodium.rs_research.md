# sources/security-integrity/cryfs/crates/crypto/src/hash/backends/libsodium.rs

## Purpose
Implements the SHA-512 hash backend using libsodium through `sodiumoxide`.

## Important APIs, types, and functions
- `LibsodiumSha512` implements `HashAlgorithmDef` with 64-byte digest and 8-byte salt.
- Implements `HashAlgorithm<64, 8>::hash`.

## Control flow
Creates a libsodium SHA-512 state, updates it with salt bytes first, then data bytes, finalizes to a digest, and returns `Hash { digest, salt }`.

## State and persistence behavior
No persistent state. It consumes the provided salt by value and returns it unchanged for storage/verification.

## Dependencies and integration points
Uses `sodiumoxide::crypto::hash::sha512::State` and shared `Digest`, `Hash`, `Salt`, and traits from the hash module. Generic tests compare it with other backends.

## Risks and edge cases
Unlike the symmetric libsodium backend, this file does not call `sodiumoxide::init`; it relies on sodiumoxide hashing being usable without explicit local init or on earlier global initialization.

## Test signals
Generic hash tests verify determinism, salt/data sensitivity, exact compatibility vectors, and empty/long data behavior for this backend.
