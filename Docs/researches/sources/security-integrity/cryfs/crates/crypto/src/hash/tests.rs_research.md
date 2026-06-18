# sources/security-integrity/cryfs/crates/crypto/src/hash/tests.rs

## Purpose
Generic test suite verifying all SHA-512 backends share identical behavior and compatibility vectors.

## Important APIs, types, and functions
- `data(size, seed)` builds deterministic random `Data`.
- Generic tests over `Hasher: HashAlgorithm<64, 8>`.
- Instantiates for `Sha512`, `OpensslSha512`, `Sha2Sha512`, and `LibsodiumSha512`.

## Control flow
Each test calls the generic hasher with fixed salts and inputs, then compares digest/salt behavior. Compatibility tests assert exact SHA-512(salt || data) hex outputs.

## State and persistence behavior
No persistent state. The exact expected digest constants are compatibility fixtures for any stored or protocol-level hashes using this algorithm.

## Dependencies and integration points
Uses `generic-tests`, `rand`, `cryfs_utils::Data`, and the hash module's public traits/types. It validates backend interchangeability.

## Risks and edge cases
Exact-vector tests intentionally make salt order and algorithm changes breaking. The tests do not cover serialization of `Hash` as a whole because the wrapper has no serializer here.

## Test signals
Signals include deterministic same-salt outputs, different salt/data outputs, empty input support, and exact digest compatibility for short, empty, and 1024-byte inputs.
