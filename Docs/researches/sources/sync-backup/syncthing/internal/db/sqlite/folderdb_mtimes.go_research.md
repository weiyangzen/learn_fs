# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_mtimes.go

## Purpose
This file persists per-file modified-time mapping pairs for a folder database.

## Important APIs and Control Flow
`GetMtime` selects `ondisk` and `virtual` nanosecond values by name and returns zero times on any error or missing row. `PutMtime` locks updates and `INSERT OR REPLACE`s the pair. `DeleteMtime` locks updates and deletes by name.

## State and Persistence Behavior
State lives in the folder DB `mtimes` table. Times are stored as `time.Time.UnixNano()` values and reconstructed with `time.Unix(0, value)`. Missing data is deliberately represented as zero times without an error path in `GetMtime`.

## Dependencies and Integration Points
The public wrappers in `db_folderdb.go` create or fetch folder DBs and delegate here. The scanner and filesystem layers likely use this to reconcile timestamp precision or virtual mtimes.

## Risks and Test Signals
Silent zero-time fallback can hide SQL errors, but keeps the API simple. `db_mtimes_test.go` covers write/read/delete round trips.
