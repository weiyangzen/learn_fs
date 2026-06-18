## sources/sync-backup/restic/internal/repository/crypto/buffer.go

Purpose: small size/buffer helpers for encrypted blob storage.

Important APIs: `NewBlobBuffer(size)` returns a slice of length `size` and capacity `size+Extension`, intended to hold plaintext and later append crypto overhead. `PlaintextLength(ciphertextSize)` subtracts `Extension`. `CiphertextLength(plaintextSize)` adds `Extension`.

Control flow and state: pure arithmetic and allocation; no validation for negative sizes or ciphertext shorter than `Extension`.

Dependencies and integration points: uses `Extension` from `crypto.go`. Repository packer and index code rely on ciphertext/plaintext length conversion for blob sizing.

Risks and test signals: callers must pass plausible non-negative sizes. Length conversion must stay in sync with the crypto construction. Coverage is indirect through crypto and repository tests.
