# sources/storage-engines/badger/y/encrypt.go

## Purpose
This file provides AES-CTR XOR helpers used for Badger encryption and decryption, plus random IV generation.

## Important APIs, Types, And Functions
`XORBlock` encrypts/decrypts from `src` into caller-provided `dst`. `XORBlockAllocate` allocates a destination and returns it. `XORBlockStream` writes transformed bytes to an `io.Writer` through `cipher.StreamWriter`. `GenerateIV` returns a random AES-block-sized IV.

## Control Flow
Each XOR helper creates an AES cipher from `key`, wraps it in CTR mode with `iv`, and applies `XORKeyStream` or `io.Copy`. Because CTR is symmetric, the same function decrypts when called with the same key and IV.

## State And Persistence Behavior
The code does not persist state directly. Correct key/IV pairing is essential for decrypting persisted Badger log/table bytes.

## Dependencies And Integration Points
It uses Go `crypto/aes`, `crypto/cipher`, `crypto/rand`, and `io`. Value-log code calls decryption through `logFile` helpers that ultimately rely on these primitives.

## Risks And Edge Cases
AES key and IV sizes are validated by the standard library. Reusing IVs with the same key would be cryptographically unsafe; this file only supplies primitives and does not enforce lifecycle policy. `XORBlockStream` wraps `io.Copy` errors with Badger's `Wrapf`.

## Test Signals
`encrypt_test.go` verifies round-trip encryption/decryption and same-slice in-place operation.
