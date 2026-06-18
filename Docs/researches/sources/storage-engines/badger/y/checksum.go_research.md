# sources/storage-engines/badger/y/checksum.go

## Purpose
This file centralizes checksum calculation and verification for Badger protobuf checksum metadata.

## Important APIs, Types, And Functions
`ErrChecksumMismatch` is the public sentinel. `CalculateChecksum` supports `pb.Checksum_CRC32C` using the shared Castagnoli table and `pb.Checksum_XXHash64` using `cespare/xxhash/v2`. `VerifyChecksum` recalculates and compares the checksum, wrapping mismatch details with `Wrapf`.

## Control Flow
Checksum calculation switches on the protobuf algorithm enum and panics for unsupported algorithms. Verification delegates to calculation, compares `actual` and `expected.Sum`, and returns nil only on exact match.

## State And Persistence Behavior
The code is stateless. It validates persisted checksum fields attached to table/log metadata elsewhere.

## Dependencies And Integration Points
It depends on Badger's `pb.Checksum` enum and `CastagnoliCrcTable` from `y.go`. It is intended for table/value-log code that stores checksums in protobuf messages.

## Risks And Edge Cases
Unsupported algorithms panic rather than returning an error, so callers must validate enums before use. `VerifyChecksum` assumes `expected` is non-nil.

## Test Signals
`checksum_test.go` verifies both algorithms, success and mismatch paths, empty CRC32C input, and unsupported algorithm panic behavior.
