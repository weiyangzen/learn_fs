# sources/sync-backup/kopia/repo/format/format_blob_cache_test.go

## Purpose
Tests format blob cache implementations for durability, overwrite timestamp updates, retrieval, and removal.

## Important APIs, Types, And Functions
`TestFormatBlobCache` table-drives `NullCache`, `DiskCache-Exists`, `DiskCache-NotExists`, and `MemoryCache` cases.

## Control Flow
Each case starts with a missing get, writes two blobs, reads the first blob, sleeps to force a later mtime, overwrites the first blob, reads it again, removes it, and checks it is gone. After subtests, it asserts disk cache removed `blob1` but retained `blob2`.

## State And Persistence
Temporary directories hold disk cache files. Memory cache stores process-local entries. Null cache discards all writes.

## Dependencies And Integration Points
Uses `clock.Now`, `testutil.TempDirectory`, `testlogging`, and `blob.ID`. Tests the public cache constructors used by format managers.

## Risks And Edge Cases
The three-second sleep makes mtime comparison robust but slow. Null cache writes return a nonzero mtime but cannot be read back, which the test codifies. The test does not inject filesystem write/remove errors.

## Test Signals
Good coverage for intended cache semantics and disk directory creation. It does not cover concurrent cache access.
