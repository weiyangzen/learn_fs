<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/decrypt.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/decrypt.rs

## Purpose
Decrypts the non-stream AEAD envelope produced by `encrypt_data`, with a plaintext pass-through fallback when crypto is not compiled.

## Important APIs, types, and functions
`decrypt_data` expects header salt(32) + alg_id(1) + nonce(12), derives a key with `ID::get_key`, selects ChaCha20Poly1305 for `Argon2idChaCHa20Poly1305` and AES-256-GCM otherwise, then calls a generic AEAD helper. Non-crypto builds return `data.to_vec()`.

## Control flow
It validates minimum 45-byte header length, parses algorithm id from byte 32, slices body after the header, converts nonce to the AEAD nonce size, and maps decrypt failures to `ErrDecryptFailed`.

## State and persistence behavior
No persistent state. The encrypted byte format is persisted by callers and must remain backward compatible.

## Dependencies and integration points
Integrates with `encdec::id`, AES-GCM, ChaCha20Poly1305, and the public crate error type.

## Risks and edge cases
Header length and algorithm id are format-critical. Non-crypto pass-through can be dangerous if the feature set is misconfigured. Wrong-password, tamper, or truncation must fail without leaking plaintext.

## Test signals
Tests cover roundtrip, wrong password, empty/large/binary/unicode data, corruption, truncation, invalid algorithm id, and feature-backed failures.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/decrypt.rs -->
