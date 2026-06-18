# sources/storage-engines/badger/y/encrypt_test.go

## Purpose
This test validates AES-CTR XOR helper symmetry and in-place behavior.

## Important APIs, Types, And Functions
`TestXORBlock` generates a 32-byte key, AES-block IV, random 1 KiB plaintext, and exercises `XORBlock`.

## Control Flow
The test encrypts `src` into `dst`, decrypts `dst` into `act`, and compares `act` to `src`. It then copies `src` into `cp`, encrypts in place, compares to `dst`, decrypts in place, and compares to the original source.

## State And Persistence Behavior
The test is in-memory only. It protects assumptions used when encrypting persisted log/table byte ranges.

## Dependencies And Integration Points
It uses Go crypto randomness, AES block sizing, and `testify/require`.

## Risks And Edge Cases
The test ignores random read errors for key, IV, and source generation. It does not exercise invalid key/IV sizes, stream writer encryption, IV generation, or cross-file integration.

## Test Signals
Failures indicate broken CTR setup, destination handling, or in-place XOR assumptions.
