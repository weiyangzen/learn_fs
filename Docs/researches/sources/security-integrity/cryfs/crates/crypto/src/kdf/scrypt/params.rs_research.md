# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/params.rs

## Purpose
Defines `ScryptParams`, the persisted binary parameters needed to reproduce scrypt-derived keys.

## Important APIs, types, and functions
- `ScryptParams { log_n, r, p, salt }` with `binrw` little-endian serialization.
- `generate`, accessors, `KDFParameters::serialize/deserialize`, and `Debug`.
- `write_log_n` serializes `log_n` as `n = 2^log_n`; `parse_log_n` validates power-of-two `n`.

## Control flow
Generation validates `log_n < 64`, creates a random salt of configured length, and stores compact `log_n`. Deserialization reads an on-disk `u64 n`, converts to `log_n`, checks exact power-of-two equivalence, then reads remaining bytes as salt.

## State and persistence behavior
This is a critical persistence format: serialized bytes are little-endian `n`, `r`, `p`, then arbitrary-length salt. Debug prints salt hex for diagnostics.

## Dependencies and integration points
Implements `KDFParameters` for the generic KDF trait. Both scrypt backends consume this type and compatibility tests pin exact serialized hex strings.

## Risks and edge cases
Salt has no minimum length validation on deserialize. `write_log_n` asserts and can panic if called with invalid internal state. Non-power-of-two stored `n` is rejected.

## Test signals
Unit tests verify generated fields and serialize/deserialize round trip. KDF tests add exact legacy serialized parameter vectors.
