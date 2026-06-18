# sources/object-store/rustfs/crates/kms/src/encryption/dek.rs

## Purpose
Provides a backend-shared interface for encrypting and decrypting data encryption keys with master key material, plus an envelope format for storing encrypted DEKs and context.

## Important APIs, Types, And Functions
`DataKeyEnvelope` stores key id, master key id, key spec, encrypted key bytes, nonce, encryption context, and creation time using compatibility time serde. `DekCrypto` is an async trait with `encrypt`, `decrypt`, `algorithm`, and `key_size`. `AesDekCrypto` implements AES-256-GCM wrapping for DEK plaintexts. `generate_key_material` creates random `AES_256` or `AES_128` key bytes.

## Control Flow
`AesDekCrypto::encrypt` validates 32-byte master key material, creates an AES-GCM cipher, generates a random 12-byte nonce, and returns ciphertext plus nonce. `decrypt` validates nonce and key material length, reconstructs the nonce array, and decrypts the ciphertext.

## State And Persistence
`DataKeyEnvelope` is the persisted/wire shape for encrypted data keys and retains the encryption context needed for authenticated decryption. It serializes `jiff::Zoned` through `time_serde::zoned`, accepting both current timezone-annotated and legacy RFC3339 strings.

## Dependencies And Integration
Uses `async_trait`, `aes_gcm`, `jiff`, `rand`, `serde`, and `HashMap`. Local and Vault KV-style backends can use this layer to wrap generated DEKs with stored master key material.

## Risks And Edge Cases
`generate_key_material` can produce `AES_128`, but `AesDekCrypto` accepts only 32-byte wrapping keys. Callers must keep key-spec usage consistent. The AEAD wrapping path does not include external AAD directly; context binding must be implemented by the envelope/backend protocol, not this encrypt call alone.

## Test Signals
Async tests cover AES DEK encrypt/decrypt round trip, invalid key and nonce sizes, key generation sizes and unsupported algorithms, envelope serde, and backward-compatible timestamp parsing.
