# sources/security-integrity/cryfs/crates/crypto/src/symmetric/aesgcm.rs

## Purpose
Defines AES-GCM type aliases and the default nonce-size policy for symmetric encryption.

## Important APIs, types, and functions
- `DefaultNonceSize = U16`.
- `LibsodiumAes256GcmNonce12` for libsodium's fixed 12-byte AES-GCM nonce.
- `AeadAes256Gcm`, `OpensslAes256Gcm`, `Aes256Gcm`, and AES-128 equivalents.

## Control flow
No runtime control flow; aliases select backend implementations and key/nonce/tag sizes through type parameters.

## State and persistence behavior
The alias selection affects ciphertext layout because nonce size is the ciphertext prefix length. Default AES-GCM uses a 16-byte nonce for random-nonce collision resistance.

## Dependencies and integration points
Feeds public exports in `symmetric/mod.rs`, compatibility tests, and benchmarks. Depends on `generic_array::typenum::U16`, `aes-gcm`, and OpenSSL backend types.

## Risks and edge cases
Changing `DefaultNonceSize` or default backend impacts ciphertext compatibility. AES-128 is documented as not recommended but still exported and tested.

## Test signals
Cipher generic tests instantiate default, 12-byte, and 16-byte nonce variants across OpenSSL/RustCrypto/libsodium where applicable.
