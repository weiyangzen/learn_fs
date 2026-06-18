# sources/sync-backup/kopia/repo/encryption/chacha20_poly1305_hmac_sha256_encryptor.go

## Purpose
Registers and implements ChaCha20-Poly1305 content encryption with per-content keys derived from HMAC-SHA256.

## Important APIs, Types, And Functions
`chacha20poly1305hmacSha256Encryptor` holds an HMAC pool. Methods mirror the AES implementation: `aeadForContent`, `Encrypt`, `Decrypt`, and `Overhead`. `init` registers `CHACHA20-POLY1305-HMAC-SHA256`.

## Control Flow
Construction derives a 32-byte HMAC secret from the repository master key. For each content ID, HMAC-SHA256 derives the ChaCha20-Poly1305 key. Encrypt/decrypt use the shared nonce-prefixed AEAD helpers with content ID as associated data.

## State And Persistence
State is an HMAC pool. Persisted ciphertext has 28 bytes overhead: 12-byte nonce plus 16-byte Poly1305 tag.

## Dependencies And Integration Points
Depends on `golang.org/x/crypto/chacha20poly1305`, HMAC/SHA256, `gather`, and the encryption registry. It is listed by `SupportedAlgorithms` and can be selected in repository content format.

## Risks And Edge Cases
Same associated-data and nonce risks as the AES implementation. The code assumes the HMAC pool returns `hash.Hash`. Algorithm availability depends on the `init` registration running.

## Test Signals
Covered by `encryption_test.go` round trips, wrong-ID/corruption failures, and known ChaCha20-Poly1305 ciphertext samples.
