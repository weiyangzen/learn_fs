# sources/user-network-fs/rclone/backend/crypt/cipher_test.go

## Purpose
This file is the primary unit-test suite for `backend/crypt/cipher.go`. It validates public and internal cipher behavior with deterministic vectors, table-driven error checks, stream round trips, and range-seek coverage.

## Important APIs, types, and functions
Tests cover `NewNameEncryptionMode`, `NameEncryptionMode.String`, `NewNameEncoding`, segment encryption/decryption, file and directory name encryption/decryption, `EncryptedSize`, `DecryptedSize`, nonce helpers, `EncryptData`, `DecryptData`, `DecryptDataSeek`, `calculateUnderlying`, stream close behavior, `getBlock`/`putBlock`, and `Key`. Helpers include `EncodingTestCase`, `testEncodeFileName`, `testEncryptSegment`, `testStandardEncryptFileName`, `testStandardDecryptFileName`, `randomSource`, `zeroes`, and `closeDetector`.

## Control flow
The first half focuses on name behavior. It verifies base32/base64/base32768 encoding vectors, invalid decode errors, standard encrypted segment vectors, encrypted file/directory paths with and without directory-name encryption, version suffix preservation, off-mode suffix behavior, and obfuscation/deobfuscation. The middle tests size formulas and nonce arithmetic, including carry propagation and adding large offsets. The later tests exercise streaming encryption/decryption with deterministic nonces and large pseudo-random data, known ciphertext vectors, error propagation from readers, truncated headers/blocks, bad magic, block authentication failure, `passBadBlocks`, close semantics, and seek/limit behavior across many offsets and limits. `TestKey` locks in scrypt-derived keys for several password/salt combinations.

## State and persistence behavior
The tests use deterministic sources to avoid external state. `randomSource` produces predictable bytes and can also validate writes. `zeroes` forces nonce generation to known values. Hard-coded `file0`, `file1`, and `file16` represent encrypted file fixtures for empty, one-byte, and sixteen-byte plaintext inputs.

## Dependencies and integration points
The suite uses `stretchr/testify` assert/require helpers, local `pkcs7` error values, base encoders, and rclone reader helpers. It directly tests unexported internals because it is in package `crypt`, which is appropriate for this low-level component.

## Risks and edge cases
The tests are thorough but computationally heavy: several stream tests copy up to `1e8` bytes. They do not fuzz arbitrary Unicode obfuscation cases or all malformed ciphertext structures, but they cover many boundary conditions. The deterministic empty-password vectors are test conveniences, not secure usage patterns.

## Test signals
This file provides strong regression signals for ciphertext format compatibility, filename compatibility, ranged decryption correctness, error behavior, and key derivation stability. It is much more focused than the generic backend `fstests` harnesses in the other researched packages.
