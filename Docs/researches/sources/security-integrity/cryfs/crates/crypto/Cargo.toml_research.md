# sources/security-integrity/cryfs/crates/crypto/Cargo.toml

## Purpose
Cargo manifest for the `cryfs-crypto` crate, declaring cryptographic primitives, backends, benchmark targets, and the optional `testutils` feature.

## Important APIs, types, and functions
- Package metadata is inherited from workspace settings.
- Runtime dependencies include OpenSSL vendored builds, sodiumoxide, RustCrypto AEAD/hash/KDF crates, `region`, `lockable`, `binrw`, and CryFS utility/version crates.
- Dev dependencies include `generic-tests`, `rstest`, and `criterion`.
- Bench targets are `hash`, `symmetric`, and `kdf` with Criterion harnesses.

## Control flow
Cargo selects the default empty feature set and always compiles all backend dependencies unless higher-level workspace features prune them elsewhere. Benchmarks are explicitly registered with `harness = false`.

## State and persistence behavior
The manifest controls dependency resolution and native OpenSSL vendoring. It stores no runtime state but affects reproducibility, binary size, and backend availability.

## Dependencies and integration points
This crate integrates with `cryfs-utils` for `Data`, `cryfs-version` for tag/version checks, OpenSSL/libsodium for native crypto, RustCrypto crates for portable backends, and Criterion for performance measurements.

## Risks and edge cases
OpenSSL is vendored, which improves build portability but increases build time and native build surface. All backend crates are hard dependencies; TODO comments in source indicate future feature-gating may be needed for production backend selection.

## Test signals
The manifest enables unit/generic tests and the three Criterion benches; no manifest-local tests exist.
