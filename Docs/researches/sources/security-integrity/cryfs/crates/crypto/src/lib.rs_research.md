# sources/security-integrity/cryfs/crates/crypto/src/lib.rs

## Purpose
Crate root for CryFS cryptographic primitives, exporting hash, KDF, and symmetric modules with strict documentation and unsafe-code policy.

## Important APIs, types, and functions
- `#![forbid(unsafe_code)]` and `#![deny(missing_docs)]`.
- Public modules `hash`, `kdf`, and `symmetric`.
- Calls `cryfs_version::assert_cargo_version_equals_git_version!()`.

## Control flow
No runtime control flow. The version assertion macro expands at compile time to enforce Cargo/git version consistency.

## State and persistence behavior
The crate root stores no state but governs public API and security posture.

## Dependencies and integration points
Integrates with `cryfs-version`; submodules connect to `cryfs-utils`, OpenSSL, sodiumoxide, and RustCrypto crates.

## Risks and edge cases
`forbid(unsafe_code)` only applies to this crate, not native/library dependencies. Missing-doc denial makes API additions require documentation.

## Test signals
Doctest examples and submodule tests/benches provide validation; the root itself has no unit tests.
