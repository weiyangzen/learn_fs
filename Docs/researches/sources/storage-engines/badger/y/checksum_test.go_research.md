# sources/storage-engines/badger/y/checksum_test.go

## Purpose
This test file validates the checksum helper contract for CRC32C and XXHash64.

## Important APIs, Types, And Functions
Tests cover `CalculateChecksum` for CRC32C and XXHash64, `VerifyChecksum` success and mismatch, and panic behavior for an unsupported `pb.Checksum_Algorithm`.

## Control Flow
Each test constructs byte slices and expected sums using the same underlying libraries, calls Badger helpers, and checks equality or error text. The unsupported algorithm test uses `defer`/`recover`.

## State And Persistence Behavior
The tests are pure in-memory but protect checksum values stored in persistent Badger metadata.

## Dependencies And Integration Points
They import `hash/crc32`, `xxhash`, `pb`, and `testify/require`.

## Risks And Edge Cases
The tests do not check nil checksum pointers or wrapped error identity with `errors.Is`; they only check message content for mismatch.

## Test Signals
Failures indicate checksum implementation drift or changed error/panic behavior.
