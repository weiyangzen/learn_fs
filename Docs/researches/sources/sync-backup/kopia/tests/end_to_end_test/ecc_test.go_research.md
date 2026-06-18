# sources/sync-backup/kopia/tests/end_to_end_test/ecc_test.go

## Purpose
Format-specific tests for error-correction-code overhead and recovery from one-byte corruption in repository blobs.

## Important APIs, Types, and Functions
`TestNoECC`, `TestECC`, `flipOneByteFromEachFile`, and `dirSize`.

## Control Flow
`TestNoECC` creates a flat repo without ECC, snapshots a 1 MiB deterministic file, and asserts repo size remains below about 1.1 MiB. `TestECC` creates a flat repo with 50 percent ECC overhead, snapshots the same data, checks v1 lacks ECC support or v2+ size grows, flips one byte in each repository file except format/shard files, then restores and compares data.

## State and Persistence Behavior
Mutates real repository blob bytes to simulate corruption. Restore should recover data when ECC is supported.

## Dependencies and Integration Points
Exercises repo format ECC settings, filesystem storage, snapshot upload, restore, and blob layout. Uses `clitestutil` to find snapshot IDs.

## Risks
Size thresholds are approximate and can be affected by format changes. Byte flipping uses random positions without deterministic seed and skips only known metadata files. The recovery check is limited to one file.

## Test Signals
Confirms ECC-disabled repositories do not incur large overhead, ECC-enabled repositories do, and corrupted blobs can still restore the original data for supported formats.
