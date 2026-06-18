# sources/sync-backup/syncthing/lib/model/fileinfobatch_test.go

## Purpose
Tests `FileInfoBatch` behavior when the flush function returns an error.

## Important APIs, Types, and Functions
`TestFileInfoBatchError` uses `NewFileInfoBatch`, `Append`, `Flush`, and `Reset`.

## Control Flow
The test first flushes successfully, then sets the flush function to return a sentinel error. It verifies the error is returned, subsequent `Flush` calls return the same error without calling the flush function again, and `Reset` clears the sticky error and pending list.

## State and Persistence Behavior
Only in-memory counters and errors are used. No database or filesystem persistence.

## Dependencies and Integration Points
Uses `protocol.FileInfo` as the batched payload type and `errors.New` for the sentinel failure.

## Risks
Does not test batch full thresholds, `FlushIfFull`, `Size`, `SetFlushFunc`, append-after-error panic, or empty flush behavior.

## Test Signals
Protects a key failure contract used by folder scanner and puller batching: once a database flush fails, callers see a stable failure until reset.
