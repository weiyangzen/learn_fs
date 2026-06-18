# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/aead.rs

## Purpose
Generic RustCrypto AEAD backend adapter implementing CryFS `Cipher`/`CipherDef` for `aead`-ecosystem ciphers.

## Important APIs, types, and functions
- `AeadCipher<C: KeyInit + AeadInPlace>` stores an `EncryptionKey`.
- `CipherDef` maps key size, nonce prefix, and tag suffix from AEAD type-level sizes.
- `encrypt`, `decrypt`, and `random_nonce`.

## Control flow
`new` validates key length. Encryption creates a cipher from key bytes, generates a random nonce, encrypts in place, grows `Data` into nonce-prefix/tag-suffix layout, and writes overhead bytes. Decryption checks minimum size, splits nonce/cipherdata/tag, verifies/decrypts in place, then shrinks to plaintext.

## State and persistence behavior
Cipher instances hold protected key material. Ciphertext format is `nonce || encrypted_payload || tag`, with no associated data.

## Dependencies and integration points
Used by AES-GCM and XChaCha20-Poly1305 RustCrypto aliases. Relies on `Data` having preallocated prefix/suffix capacity for no-reallocation growth.

## Risks and edge cases
Encryption panics if `Data` lacks sufficient reserved prefix/suffix capacity. Cipher construction is repeated per operation. No associated data is authenticated, so all metadata integrity must be handled elsewhere.

## Test signals
Shared cipher tests cover round trips, tamper failure, too-small ciphertext failure, nonce nondeterminism, backend interoperability, and compatibility ciphertext vectors.
