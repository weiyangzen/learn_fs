# sources/object-store/rustfs/crates/kms/src/encryption/ciphers.rs

## Purpose
Implements AEAD object-data ciphers used after KMS produces a plaintext data key. It provides a common trait over AES-256-GCM and ChaCha20-Poly1305 and helpers for cipher construction and IV generation.

## Important APIs, Types, And Functions
`ObjectCipher` defines `encrypt`, `decrypt`, `algorithm`, `key_size`, `iv_size`, and `tag_size`. `AesCipher::new` and `ChaCha20Cipher::new` validate 32-byte keys and wrap the crypto library cipher instances. `create_cipher` maps `EncryptionAlgorithm::Aes256` and `AwsKms` to AES-256-GCM, and `ChaCha20Poly1305` to ChaCha20-Poly1305. `generate_iv` returns a random 12-byte nonce/IV for all supported algorithms.

## Control Flow
Encryption validates IV length, constructs a nonce, runs AEAD encryption with supplied AAD, then splits the library's ciphertext-plus-tag into separate ciphertext and 16-byte tag. Decryption validates IV and tag lengths, recombines ciphertext and tag, and calls AEAD decrypt with matching AAD.

## State And Persistence
Cipher structs hold initialized cipher state only; no persistence. Generated IVs and authentication tags are returned to callers and later stored in object encryption metadata.

## Dependencies And Integration
Depends on `aes_gcm`, `chacha20poly1305`, `rand`, `KmsError`, and `EncryptionAlgorithm`. `service.rs` uses `create_cipher` and `generate_iv` for SSE-S3, SSE-KMS, and SSE-C object encryption/decryption.

## Risks And Edge Cases
`AwsKms` is implemented as AES-256-GCM at the object cipher layer, which is reasonable because KMS wraps the DEK rather than encrypting object bytes remotely. Nonce reuse under the same key would be catastrophic for AEAD security; this file uses random IV generation, so call sites must not override it with repeated IVs. Error reporting reuses `invalid_key_size` for invalid IV/tag sizes, which may be semantically confusing.

## Test Signals
Tests cover AES and ChaCha encrypt/decrypt round trips with AAD, factory selection, random IV length and uniqueness, invalid key sizes, and invalid IV size rejection.
