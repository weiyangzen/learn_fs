# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/openssl.rs

## Purpose
OpenSSL AEAD backend adapter for AES-128-GCM and AES-256-GCM.

## Important APIs, types, and functions
- `CipherType` trait defines key size, nonce size, auth tag size, and OpenSSL cipher instantiation.
- `Aes256Gcm<NonceSize>` and `Aes128Gcm<NonceSize>` implement `CipherType`.
- `AeadCipher<C: CipherType>` implements `CipherDef` and `Cipher`.

## Control flow
Constructor validates key length and stores an OpenSSL cipher handle. Encryption generates a random nonce and tag, calls `encrypt_aead`, copies output back into the original `Data`, grows prefix/suffix overhead, and writes nonce/tag. Decryption validates size, splits nonce/cipherdata/tag, calls `decrypt_aead`, shrinks the `Data`, and copies plaintext back.

## State and persistence behavior
Cipher instances hold protected key bytes and an OpenSSL cipher descriptor. Ciphertexts use the common `nonce || ciphertext || tag` format with configurable nonce length and 16-byte tag.

## Dependencies and integration points
Default AES-GCM aliases point here. Interoperability tests compare OpenSSL outputs with RustCrypto and libsodium formats.

## Risks and edge cases
OpenSSL operations allocate separate output buffers, so performance includes copy-back costs. Encryption still requires preallocated `Data` overhead or panics on growth. No associated data is supplied.

## Test signals
Generic cipher tests cover OpenSSL AES-128/256 with default, 12-byte, and 16-byte nonces, cross-backend decryption, tamper failures, and fixed compatibility ciphertexts.
