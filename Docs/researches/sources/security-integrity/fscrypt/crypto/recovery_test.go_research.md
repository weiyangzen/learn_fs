# sources/security-integrity/fscrypt/crypto/recovery_test.go

## Purpose
This test file validates recovery-code encoding and decoding for fscrypt policy keys. It ensures recovery strings are stable, reversible, and rejected when malformed.

## Important APIs, Types, and Functions
Helpers include `getRecoveryCodeFromKey`, `getRandomRecoveryCodeBuffer`, `getKeyFromRecoveryCode`, `testKeyEncodeDecode`, and `testRecoveryDecodeEncode`. Tests include `TestFakeSecretKey`, `TestEncodeDecode`, `TestDecodeEncode`, `TestWrongLengthError`, `TestBadCharacterError`, and `TestBadEndCharacterError`. Benchmarks cover encode, decode, encode/decode, and decode/encode paths.

## Control Flow
The tests construct or generate policy-length keys, call `WriteRecoveryCode`, read them back through `ReadRecoveryCode`, and compare raw key bytes or recovery-code bytes. Negative tests mutate key length, a base32 character, or the separator byte and assert decoding or encoding fails.

## State and Persistence
All state is in memory. Random keys are wiped with `defer key.Wipe()` where applicable. A package-level `fakeSecretKey` and expected string encode a deterministic fixture.

## Dependencies and Integration Points
Uses `metadata.PolicyKeyLen` and the crypto package's key construction helpers. It directly validates the public recovery-code API used by recovery workflows outside this package.

## Risks
The package-level fake key is deliberately insecure and marked testing-only. These tests do not validate user-interface handling, storage of recovery codes, or all possible truncation/extra-data cases.

## Test Signals
The file is itself the test signal: it confirms deterministic encoding of a known key, randomized round trips in both directions, rejection of short keys, rejection of lowercase base32, and rejection of bad separators.
