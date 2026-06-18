# sources/sync-backup/kopia/repo/ecc/ecc_rs_crc_test.go

## Purpose
Validates Reed-Solomon CRC ECC sizing and recovery behavior for small, medium, and large payloads.

## Important APIs, Types, And Functions
Tests include `Test_RsCrc32_AssertSizeAlwaysGrow` (skipped by default), `Test_RsCrc32_2p_1b`, `Test_RsCrc32_2p_10kb`, and `Test_RsCrc32_10p_1mb`. Helpers mutate data shard bytes, data CRC bytes, parity shard bytes, and parity CRC bytes, then call shared `testPutAndGet`.

## Control Flow
Each active test creates ECC options, encrypts generated deterministic data, asserts final length, flips configured bytes in stored data, then decrypts and expects success or failure depending on parity capacity. The skipped monotonic test walks sizes up to 10 MiB, ensuring computed stored sizes do not decrease and stored-size decoding reproduces original sizing.

## State And Persistence
State is in-memory byte slices and `gather.WriteBuffer`s. There is no external storage.

## Dependencies And Integration Points
Uses `testutil.EnsureType` to inspect the concrete `ReedSolomonCrcECC`, and `CreateAlgorithm` to exercise registration rather than direct construction for active tests.

## Risks And Edge Cases
The tests encode important expected ECC overhead sizes, so implementation changes that alter layout will break them. They verify both recoverable and unrecoverable corruption thresholds. The slow monotonic test is skipped, so broad size regression coverage is manual unless enabled.

## Test Signals
Coverage is strong for representative payload sizes and corruption locations. It does not cover malformed truncated ECC streams beyond changed-byte scenarios.
