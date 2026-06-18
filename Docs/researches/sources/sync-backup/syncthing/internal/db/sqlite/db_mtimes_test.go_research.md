# sources/sync-backup/syncthing/internal/db/sqlite/db_mtimes_test.go

## Purpose
This test file covers folder-scoped modified-time pair persistence. Syncthing stores both on-disk and virtual mtimes for a file name.

## Important APIs and Control Flow
`TestMtimePairs` opens a temporary DB, writes a pair using `PutMtime(folder, name, ondisk, virtual)`, reads it through `GetMtime`, deletes it with `DeleteMtime`, and verifies reads return zero times after deletion.

## State and Persistence Behavior
The test exercises the `mtimes` table in the folder DB. Times are stored as Unix nanoseconds by `folderDB.PutMtime` and reconstructed with `time.Unix(0, nanos)`. `PutMtime` creates the folder DB if needed; `DeleteMtime` and `GetMtime` are tolerant of missing rows.

## Dependencies and Integration Points
The file uses the public `DB` wrapper methods in `db_folderdb.go`, which delegate to `folderdb_mtimes.go`, and Go's `time` package.

## Risks and Test Signals
The main risk is lossy or mismatched time serialization. The test truncates one value to second precision and uses a nanosecond offset for the other, giving coverage for both simple and subsecond values. It does not cover cross-platform path normalization.
