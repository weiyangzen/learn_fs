# sources/sync-backup/kopia/repo/format/encryptor_wrapper.go

## Purpose
Composes two `encryption.Encryptor` implementations, typically content encryption followed by ECC, into a single encryptor for the format provider.

## Important APIs, Types, And Functions
`encryptorWrapper` stores `impl` and `next`. It implements `Encrypt`, `Decrypt`, and `Overhead`.

## Control Flow
Encryption runs `impl.Encrypt` into a temporary buffer, then passes that ciphertext through `next.Encrypt`. Decryption reverses the order: `next.Decrypt` first, then `impl.Decrypt`. `Overhead` panics because composed ECC overhead can be variable and callers should not request fixed overhead from this wrapper.

## State And Persistence
No independent persistence. The persisted bytes are the nested output of the two encryptors.

## Dependencies And Integration Points
Used by `NewFormattingOptionsProvider` when content format enables ECC. Depends on `gather` and `repo/encryption`.

## Risks And Edge Cases
Order is significant: ECC protects encrypted bytes, not plaintext. Any caller that invokes `Overhead` on a wrapper will panic. Temporary buffers are correctly closed, but errors are passed through without additional context.

## Test Signals
ECC and encryption tests cover the individual transforms; this wrapper is indirectly exercised when repository formats enable ECC outside this subset.
