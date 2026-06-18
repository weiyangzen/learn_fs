# sources/sync-backup/kopia/repo/ecc/ecc_utils_test.go

## Purpose
Tests ECC utility shard calculations and provides shared round-trip/corruption helpers for ECC tests.

## Important APIs, Types, And Functions
`TestComputeShares` verifies `computeShards` for 0.1%, 1%, 2%, and 10% overhead. `testPutAndGet` creates an ECC algorithm, encrypts deterministic data, mutates it through a callback, and decrypts. `flipByte` forces a byte to an opposite extreme value.

## Control Flow
Round-trip helper generates nonzero deterministic payload bytes, encrypts into a write buffer, checks expected size increase, applies caller mutations, decrypts, and asserts either recovered equality or an error.

## State And Persistence
Only in-memory buffers and slices are used.

## Dependencies And Integration Points
Uses `gather`, `repo/encryption` interface, and `CreateAlgorithm`, so tests exercise the registry/factory path.

## Risks And Edge Cases
Shard-count tests pin the floor/clamp behavior. Shared helper assumes `expectedEccSize` equals stored length minus original size, so layout changes require test updates.

## Test Signals
Useful support coverage for ECC implementation. It does not independently test every numeric helper, but most are exercised through Reed-Solomon tests.
