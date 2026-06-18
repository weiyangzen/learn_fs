# sources/sync-backup/kopia/repo/format/format_blob_test.go

## Purpose
Tests recovery of checksummed format blob bytes from standalone blobs and blobs with extra prefix or suffix bytes.

## Important APIs, Types, And Functions
`TestFormatBlobRecovery` uses `addFormatBlobChecksumAndLength` and `RecoverFormatBlob`.

## Control Flow
The test creates checksummed bytes from sample data, stores them as a standalone blob, as a suffix after extra bytes, and as a prefix before extra bytes. It also stores a corrupted checksum, a missing-name case, and blobs of length zero through five. Each case asserts either recovered original bytes or the expected error.

## State And Persistence
Uses `blobtesting.DataMap` and map storage to persist test blobs.

## Dependencies And Integration Points
Uses `gather`, `blob.PutOptions`, `testlogging`, and `pkg/errors` for `errors.Is`. It directly validates format blob recovery used when repository format bytes are embedded in pack data.

## Risks And Edge Cases
The test covers too-short blobs and bad checksums. It does not cover multiple blobs matching a prefix or explicit optional length values other than `-1`.

## Test Signals
Good focused coverage for recovery boundary behavior and checksum validation.
