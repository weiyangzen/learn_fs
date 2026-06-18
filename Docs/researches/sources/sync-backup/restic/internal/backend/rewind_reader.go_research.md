<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rewind_reader.go -->
# sources/sync-backup/restic/internal/backend/rewind_reader.go

## Purpose
Defines rewindable readers used by Save so retry wrappers can replay uploads and backends can know length/hash.

## Important APIs, Types, And Functions
RewindReader, ByteReader, NewByteReader, FileReader, and NewFileReader are the API.

## Control Flow
ByteReader wraps bytes.Reader, precomputes optional hash, exposes Rewind/Length/Hash. FileReader wraps an io.ReadSeeker, records length from SeekEnd, rewinds to start, and returns a supplied hash.

## State And Persistence Behavior
State is reader position, byte buffer/file seeker, length, and hash. No repository persistence.

## Dependencies And Integration Points
Depends on bytes, hash, io, and internal/errors.

## Risks And Edge Cases
Hash may be nil when backend does not need content hash. FileReader requires seekable input and correct external hash.

## Test Signals
rewind_reader_test.go validates byte and file rewind/read semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rewind_reader.go -->
