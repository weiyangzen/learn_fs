# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/libsodium.rs

## Purpose
libsodium-backed AEAD implementations for AES-256-GCM and XChaCha20-Poly1305.

## Important APIs, types, and functions
- `init_libsodium` guarded by `Once`.
- `Aes256Gcm` with `is_available`, `CipherDef`, and `Cipher`.
- `XChaCha20Poly1305` with `CipherDef` and `Cipher`.
- Shared `_encrypt`, `_decrypt`, and key conversion helpers.

## Control flow
Constructors validate key length and initialize libsodium; AES-GCM also creates an `Aes256Gcm` object that may require hardware support. Encryption generates a nonce, seals plaintext in place, grows `Data` to store nonce prefix and tag suffix, then returns ciphertext. Decryption validates length, splits overhead, reconstructs libsodium nonce/tag types, verifies/decrypts in place, and shrinks to plaintext.

## State and persistence behavior
Global libsodium initialization is process-wide and one-time. Cipher instances hold protected `EncryptionKey`. Ciphertext format is shared with other backends: nonce prefix, encrypted payload, tag suffix.

## Dependencies and integration points
Provides public aliases for libsodium AES-GCM and default XChaCha20-Poly1305. Interoperability tests cross-decrypt with RustCrypto and OpenSSL where formats match.

## Risks and edge cases
AES-GCM constructor panics if called without checking hardware availability. Encryption panics when `Data` lacks reserved overhead capacity. Associated data is `None`, so metadata binding is not provided here.

## Test signals
Generic cipher tests validate libsodium round trips, tamper/short-ciphertext failures, random nonce behavior, compatibility vectors, and cross-backend interoperability for XChaCha20 and 12-byte AES-GCM on supported architectures.
