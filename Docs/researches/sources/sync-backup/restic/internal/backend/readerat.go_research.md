<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/readerat.go -->
# sources/sync-backup/restic/internal/backend/readerat.go

## Purpose
Provides io.ReaderAt access over the backend Load API.

## Important APIs, Types, And Functions
backendReaderAt, ReaderAt, and ReadAt are the API.

## Control Flow
ReadAt logs the read, calls backend.Load for len(p) at offset, uses io.ReadFull in the consumer, and translates EOF/short read behavior into ReaderAt-compatible results.

## State And Persistence Behavior
No persistence; carries context/backend/handle for the lifetime of the reader.

## Dependencies And Integration Points
Depends on context, io, backend.Backend/Handle, debug, and errors.

## Risks And Edge Cases
The returned ReaderAt should not escape the caller because it embeds a context that may be canceled.

## Test Signals
Covered indirectly by backend load tests and code paths that require random access.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/readerat.go -->
