# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/mod.rs

## Purpose
Namespace for scrypt KDF backend implementations.

## Important APIs, types, and functions
- Public submodules `openssl` and `scrypt`.
- Documents `ScryptScrypt` and `ScryptOpenssl` choices.

## Control flow
No runtime control flow; it exposes backend modules.

## State and persistence behavior
No state.

## Dependencies and integration points
Parent `scrypt` module aliases the pure Rust backend as default, while tests and benchmarks import both modules through this namespace.

## Risks and edge cases
TODO notes indicate backend feature selection is not yet configurable by Cargo features.

## Test signals
Backend correctness is tested via generic KDF tests instantiated for both concrete backend types.
