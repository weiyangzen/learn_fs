<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/encrypt.rs -->
# sources/object-store/rustfs/crates/crypto/src/encdec/encrypt.rs

## Purpose
Encrypts arbitrary bytes into a compact AEAD envelope with random salt and nonce, with a plaintext fallback when crypto is not compiled.

## Important APIs, types, and functions
`encrypt_data` generates a 32-byte salt, chooses `ID::Pbkdf2AESGCM` under `fips`, otherwise chooses Argon2id AES-GCM when `native_aes()` is true or Argon2id ChaCha20Poly1305 otherwise. `encrypt` creates a random nonce, AEAD-encrypts the data, and outputs salt + id + nonce + ciphertext/tag.

## Control flow
The generic helper reserves output capacity, appends header fields, and maps AEAD errors to `ErrEncryptFailed`. Non-crypto builds return a plaintext copy.

## State and persistence behavior
No persistent state, but the emitted envelope is a storage format consumed by `decrypt_data`.

## Dependencies and integration points
Integrates with CPU AES detection, algorithm id/key derivation, AES-GCM, ChaCha20Poly1305, rand, and FIPS feature selection.

## Risks and edge cases
Random salt/nonce generation is security-critical. The non-crypto fallback must never be used unintentionally for protected data. Algorithm choice must remain compatible with decrypt and persisted ids.

## Test signals
Tests assert distinct ciphertext for same input, envelope structure, many input/password forms, large data, concurrency, and decrypt compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/encdec/encrypt.rs -->
