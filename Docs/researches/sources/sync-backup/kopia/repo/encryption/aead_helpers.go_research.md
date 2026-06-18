# sources/sync-backup/kopia/repo/encryption/aead_helpers.go

## Purpose
Contains shared AEAD sealing/opening helpers for encryption algorithms that prepend random nonces and authenticate content IDs as associated data.

## Important APIs, Types, And Functions
Private helpers are `aeadSealWithRandomNonce` and `aeadOpenPrefixedWithNonce`.

## Control Flow
Seal allocates one contiguous buffer containing nonce plus plaintext/ciphertext space, fills the nonce with `crypto/rand`, appends plaintext into the buffer, calls `AEAD.Seal` with content ID as associated data, and appends the whole nonce+ciphertext to output. Open checks minimum length, copies ciphertext into a contiguous buffer, splits nonce and ciphertext, calls `AEAD.Open` with the same content ID, and appends plaintext to output.

## State And Persistence
No persistent state. The nonce is persisted as the ciphertext prefix by callers.

## Dependencies And Integration Points
Depends on `crypto/cipher`, `crypto/rand`, `gather`, and `pkg/errors`. Used by AES-GCM-HMAC-SHA256 and ChaCha20-Poly1305-HMAC-SHA256 encryptors.

## Risks And Edge Cases
Random nonce generation failure aborts encryption. Decrypt rejects ciphertext shorter than nonce plus AEAD tag. Associated-data binding means decrypting with a wrong content ID fails, which is central to repository integrity.

## Test Signals
`encryption_test.go` indirectly covers random nonces, wrong content IDs, corrupted ciphertexts, short/corrupt authentication failures, and known ciphertext samples.
