<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/id.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/id.rs

## Purpose
Defines encrypted-format algorithm identifiers and password-to-key derivation.

## Important APIs, types, and functions
`ID` is a `repr(u8)` enum: `Argon2idAESGCM=0x00`, `Argon2idChaCHa20Poly1305=0x01`, and `Pbkdf2AESGCM=0x02`. `TryFrom<u8>` validates persisted ids. `get_key` derives a 32-byte key using PBKDF2-HMAC-SHA256 with 8192 iterations or Argon2id v1.3 with 64 MiB memory, 1 iteration, parallelism 4, output length 32.

## Control flow
Callers parse the id from encrypted data, then call `get_key(password, salt)` before constructing the selected AEAD.

## State and persistence behavior
No state. The numeric ids are persisted in encrypted headers and cannot change without migration.

## Dependencies and integration points
Integrates with encrypt/decrypt, stream_io, PBKDF2, Argon2, SHA256, and crate error conversion.

## Risks and edge cases
Changing id values or KDF parameters breaks old encrypted data or changes security/performance. Argon2 memory cost can be expensive under concurrency. Empty password/salt are currently allowed by tests, so callers must enforce policy if needed.

## Test signals
Unit tests cover id values, valid/invalid conversion, key determinism, different password/salt behavior, all algorithms, empty inputs, and cross-algorithm differences.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/id.rs -->
