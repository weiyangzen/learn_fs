# sources/sync-backup/kopia/repo/encryption/encryption_test.go

## Purpose
Tests all registered encryption algorithms for round-trip correctness, nonce non-determinism, content-ID authentication, corruption detection, known-sample compatibility, and benchmark performance.

## Important APIs, Types, And Functions
The local `parameters` type implements `encryption.Parameters`. Tests are `TestRoundTrip`, `TestCiphertextSamples`, `verifyCiphertextSamples`, and `BenchmarkEncryption`.

## Control Flow
`TestRoundTrip` generates random data, master key, and two content IDs, then encrypts/decrypts with every supported algorithm. It asserts repeated encryption differs, correct IDs decrypt successfully, different content IDs produce different ciphertext, wrong IDs fail, and bit flips fail. `TestCiphertextSamples` decodes known ciphertext hex strings and verifies they decrypt to expected payloads for each algorithm.

## State And Persistence
All state is in-memory random bytes and buffers. Known sample ciphertexts act as compatibility fixtures.

## Dependencies And Integration Points
Uses the public encryption registry and `gather.WriteBuffer`, so it tests the same construction path used by repository format code.

## Risks And Edge Cases
Randomness means exact ciphertext output is not asserted for new encryptions; samples only test decryption compatibility. The corruption test mutates one slice inside `gather.Bytes`, assuming at least one slice and non-empty ciphertext.

## Test Signals
Strong coverage for confidentiality/integrity API behavior across algorithms. Benchmark covers default encryption throughput for an 8 MiB payload.
