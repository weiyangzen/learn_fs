# sources/storage-engines/tikv/components/crypto/src/lib.rs

Purpose: This crate root describes `crypto` as a FIPS-conscious shim for cryptographic operations and exports the concrete modules currently implemented.

Important APIs and modules: It publicly exposes `fips` and `rand`. The documentation calls out random-number generation and leaves message-digest support as a TODO.

Control flow: There is no runtime control flow in this file.

State and persistence behavior: No state is defined here.

Dependencies and integration points: Downstream crates import `crypto::fips` for process setup and `crypto::rand` for OpenSSL-backed randomness, avoiding direct use of non-FIPS RNGs in encryption paths.

Risks: The crate is intentionally small; adding cryptographic helpers here should preserve FIPS semantics and avoid accidental use of non-approved providers.

Test signals: Module-level tests, if any, live in submodules.
