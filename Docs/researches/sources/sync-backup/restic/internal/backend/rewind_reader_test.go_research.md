<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rewind_reader_test.go -->
# sources/sync-backup/restic/internal/backend/rewind_reader_test.go

## Purpose
Tests ByteReader and FileReader rewind, length, and content behavior.

## Important APIs, Types, And Functions
TestByteReader, TestFileReader, and testRewindReader are the main tests.

## Control Flow
The tests read data, rewind, reread, and compare expected bytes and lengths for in-memory and temp-file readers.

## State And Persistence Behavior
Uses temporary files for FileReader.

## Dependencies And Integration Points
Depends on backend readers, bytes/io/os, and testing helpers.

## Risks And Edge Cases
Hash behavior is lightly covered through construction rather than deep validation.

## Test Signals
Good unit signal for retry-safe upload readers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rewind_reader_test.go -->
