# sources/security-integrity/cryfs/crates/crypto/src/hash/mod.rs

## Purpose
Top-level hash module defining the hash traits, exporting hash value types, and selecting the default SHA-512 backend.

## Important APIs, types, and functions
- Traits `HashAlgorithmDef` and `HashAlgorithm<const DIGEST_LEN, const SALT_LEN>`.
- Re-exports `Digest`, `Hash`, `Salt`, and concrete backend types.
- `pub type Sha512 = backends::OpensslSha512`.

## Control flow
No runtime control flow. Implementations call `HashAlgorithm::hash` with explicit salt and input data.

## State and persistence behavior
The module defines no state. It establishes the persistent hash format contract: digest bytes plus salt bytes, with salt prepended before hashing.

## Dependencies and integration points
Used by benchmarks, tests, and downstream CryFS integrity code. It centralizes backend choice while still exposing alternatives.

## Risks and edge cases
TODO comments flag possible hardening by increasing salt size or switching to SHA3. The default backend selection is a type alias, so changing it must preserve exact digest compatibility or migrate stored data.

## Test signals
`hash/tests.rs` uses generic instantiations for default and concrete backends to enforce parity.
