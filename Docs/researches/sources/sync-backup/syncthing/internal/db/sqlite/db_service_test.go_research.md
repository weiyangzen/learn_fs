# sources/sync-backup/syncthing/internal/db/sqlite/db_service_test.go

## Purpose
This test file validates deterministic blob-range SQL generation used by database maintenance garbage collection.

## Important APIs and Control Flow
`TestBlobRange` calls `blobRanges(7)`, formats each range with `blobRange.SQL("hash")`, and compares the output against expected open/closed half-open ranges over three-byte prefixes.

## State and Persistence Behavior
No database is opened. The test covers the SQL fragments used by `garbageCollectBlocklistsAndBlocksLocked` to partition deletes over `blocks.hash` or `blocklists.blocklist_hash`.

## Dependencies and Integration Points
The test uses `bytes.Buffer`, `fmt.Fprintln`, and `strings.TrimSpace`. It directly exercises `blobRanges`, `blobRange.SQL`, and indirectly `intToBlob` in `db_service.go`.

## Risks and Test Signals
The risk is malformed SQL ranges that overlap, leave gaps, or produce unbounded deletes. The test confirms the first range has only an upper bound, middle ranges have both bounds, and the last range has only a lower bound.
