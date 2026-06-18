## sources/sync-backup/restic/internal/repository/crypto/crypto_int_test.go

Purpose: internal-package tests for low-level Poly1305 and deterministic crypto behavior.

Important tests/helpers: `poly1305Tests` contains published Poly1305-AES vectors. `TestPoly1305` verifies MAC generation and verification. `testValues` includes a known key/ciphertext/plaintext sample. `decodeArray16`, `decodeArray32`, and `decodeHex` build fixtures. `TestCrypto` checks encrypt/decrypt, MAC tampering, nonce tampering, ciphertext tampering, and decoding known ciphertext. `TestNonceValid` and `BenchmarkNonceValid` cover nonce validation.

Control flow and state: tests mutate ciphertext and nonce bytes in place, then restore them where needed. They call unexported crypto helpers by staying in package `crypto`.

Dependencies and integration points: validates assumptions that repository pack encryption relies on. No repository I/O is involved.

Risks and test signals: strong signal for cryptographic compatibility and tamper detection. It does not test concurrent use or nonce uniqueness policy, which must be enforced by callers.
