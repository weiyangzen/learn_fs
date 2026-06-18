# sources/security-integrity/cryfs/crates/crypto/src/hash/digest.rs

## Purpose
Defines the fixed-size digest wrapper used as the output of hash algorithms.

## Important APIs, types, and functions
- `Digest<const DIGEST_LEN: usize>([u8; DIGEST_LEN])`.
- `new`, `to_hex`, and `from_hex`.
- Custom `Debug` prints the digest as hex inside a tuple.

## Control flow
`from_hex` decodes the full input with `hex::decode`, checks exact byte length, copies into a fixed array, and returns `InvalidStringLength` when the decoded byte count differs.

## State and persistence behavior
Digest is copyable immutable byte state. Hex encoding/decoding is the storage/display boundary and always uses lowercase output from `hex::encode`.

## Dependencies and integration points
Used by all hash backends and by `Hash`. Compatibility tests compare `to_hex()` values.

## Risks and edge cases
`from_hex` allocates a temporary `Vec` before length validation. It rejects wrong decoded byte length but reports the generic hex length error rather than a custom digest-size error.

## Test signals
Unit tests cover round trip, invalid length, invalid characters, debug formatting, and a full exact hex pattern.
