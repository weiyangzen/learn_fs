# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/tests.rs

## Purpose
Generic test suite ensuring scrypt backends produce reproducible and backward-compatible keys.

## Important APIs, types, and functions
- Tests over `S: PasswordBasedKDF<Settings = ScryptSettings, Parameters = ScryptParams>`.
- Instantiates default `Scrypt`, `ScryptScrypt`, and `ScryptOpenssl`.
- Uses `KDFParameters::serialize/deserialize` and exact hex fixtures.

## Control flow
Tests generate parameters, derive keys of 56, 32, and 16 bytes, serialize/deserialize parameters, and re-derive. Compatibility tests deserialize fixed parameter hex and compare exact derived key hex.

## State and persistence behavior
Fixed serialized parameter vectors represent the durable on-disk KDF contract. Tests also verify password byte handling for empty, Unicode, and long passwords.

## Dependencies and integration points
Exercises both backend implementations through the shared trait and confirms `EncryptionKey::to_hex` values.

## Risks and edge cases
The default-settings compatibility test can be slower because it uses expensive production settings. Tests expect uppercase key hex from `EncryptionKey::to_hex`.

## Test signals
Signals include key reproducibility after parameter serialization, exact legacy key vectors for multiple key sizes, password sensitivity, empty/unicode/long password support, and backend parity.
