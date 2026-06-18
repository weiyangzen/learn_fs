# sources/security-integrity/cryfs/crates/crypto/benches/symmetric.rs

## Purpose
Criterion benchmark for symmetric encryption and decryption across AES-GCM and XChaCha20-Poly1305 backends.

## Important APIs, types, and functions
- `make_key`, `make_plaintext`, and `make_ciphertext` produce deterministic keys/data with required `Data` prefix/suffix capacity.
- Benchmarks default, OpenSSL, RustCrypto AEAD, and libsodium variants for AES-128-GCM, AES-256-GCM, and XChaCha20-Poly1305.
- Uses `LibsodiumAes256GcmNonce12::is_available` to skip unsupported hardware.

## Control flow
For each payload size, encryption cases construct a cipher and plaintext then measure `encrypt(plaintext.clone())`. Decryption cases pre-encrypt once then measure `decrypt(ciphertext.clone())`.

## State and persistence behavior
No persistent state. Randomness is deterministic for input/key generation, while encryption nonces are generated inside the measured operation.

## Dependencies and integration points
Stresses the public `Cipher`/`CipherDef` APIs, `EncryptionKey`, `Data` region growth, and backend interoperability choices exposed by type aliases.

## Risks and edge cases
Benchmarks include clone costs for `Data` and may include nonce generation overhead. Libsodium AES-GCM only runs when available, so result sets differ by CPU. The helper requires correctly preallocated `Data`; otherwise encryption implementations can panic on failed no-reallocation growth.

## Test signals
Criterion timings for encryption/decryption by size and backend; not a correctness oracle.
