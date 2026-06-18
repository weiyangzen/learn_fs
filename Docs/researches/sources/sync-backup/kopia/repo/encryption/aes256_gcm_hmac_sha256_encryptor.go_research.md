# sources/sync-backup/kopia/repo/encryption/aes256_gcm_hmac_sha256_encryptor.go

## Purpose
Registers and implements the default AES-256-GCM content encryption algorithm with per-content keys derived from HMAC-SHA256.

## Important APIs, Types, And Functions
Constants define fixed overhead and key-derivation secret size. `aes256GCMHmacSha256` holds an HMAC hash pool. Methods are `aeadForContent`, `Encrypt`, `Decrypt`, and `Overhead`. `init` registers `AES256-GCM-HMAC-SHA256`.

## Control Flow
At construction, `deriveKey` creates a 32-byte secret for HMAC. For each content ID, `aeadForContent` hashes the content ID with pooled HMAC-SHA256 to derive a 32-byte AES key, creates an AES cipher, and wraps it in GCM. Encrypt/decrypt delegate to the AEAD helper functions with random nonce prefixing and content-ID associated data.

## State And Persistence
The encryptor stores only an HMAC pool. Persisted ciphertext layout is nonce-prefixed AEAD output with 28 bytes of fixed overhead: 12-byte GCM nonce plus 16-byte tag.

## Dependencies And Integration Points
Depends on standard AES/GCM/HMAC/SHA256 and the package registry. It is the `encryption.DefaultAlgorithm` used by format/content tests and default repository formats.

## Risks And Edge Cases
Security depends on high-quality random nonces and distinct content-ID-derived keys. The HMAC pool uses type assertion and must only contain hash.Hash values from its own `New` function. Wrong master keys or content IDs surface as decrypt authentication failures.

## Test Signals
`encryption_test.go` verifies round trips, ciphertext non-determinism, wrong content ID failure, mutation failure, and known AES sample decryptions.
