# sources/security-integrity/cryfs/crates/crypto/src/hash/salt.rs

## Purpose
Defines the fixed-size salt wrapper for hash operations.

## Important APIs, types, and functions
- `Salt<const SALT_LEN: usize>([u8; SALT_LEN])`.
- `new`, `get`, `to_hex`, `from_hex`, and `generate_random`.
- Derives `derive_more::From` for raw array conversion.

## Control flow
`from_hex` decodes and length-checks, then copies into the fixed array. `generate_random` fills the array using `rand::rng().random()`.

## State and persistence behavior
Salt is copyable byte state, usually persisted alongside a digest. Hex output is lowercase; debug output reveals the salt in hex, which is acceptable because salts are non-secret.

## Dependencies and integration points
Consumed by all hash backends, tests, and benchmarks. It is part of the `Hash` return value.

## Risks and edge cases
Randomness source is `rand`'s default RNG interface. Tests assert two generated salts differ, which has an astronomically small false-failure probability for 8-byte salts.

## Test signals
Unit tests cover hex round trip, invalid length, random inequality, debug formatting, and an exact byte-to-hex mapping.
