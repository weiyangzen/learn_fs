# sources/security-integrity/cryfs/crates/crypto/src/hash/backends/mod.rs

## Purpose
Backend aggregator for hash algorithms, exposing OpenSSL, RustCrypto `sha2`, and libsodium SHA-512 implementations.

## Important APIs, types, and functions
- Declares `openssl`, `sha2`, and `libsodium` submodules.
- Re-exports `OpensslSha512`, `Sha2Sha512`, and `LibsodiumSha512`.

## Control flow
This module has no runtime control flow; it is a compile-time namespace and public re-export layer.

## State and persistence behavior
No state.

## Dependencies and integration points
Feeds the parent `hash` module's public API and default type alias. Benchmarks and tests import concrete backend types through this module.

## Risks and edge cases
All backends are compiled as normal modules; backend dependency failures affect the whole crate until future feature-gating is introduced.

## Test signals
Coverage comes from backend-specific generic tests instantiated in `hash/tests.rs`.
