# sources/sync-backup/syncthing/internal/db/sqlite/db_open.go

## Purpose
This file defines the top-level SQLite `DB` type and open/close lifecycle for Syncthing's SQLite database backend.

## Important APIs and Types
`DB` embeds `*baseDB` for the main database and tracks `pathBase`, `deleteRetention`, an RW-locked `folderDBs` map, and a `folderDBOpener`. `Option` and `WithDeleteRetention` configure deleted-file retention, clamping positive durations to at least 24 hours. `Open` configures WAL, optimization, incremental vacuum, and the main application ID, runs schema/migrations, cleans dropped folder files, and opens existing folder DBs. `OpenForMigration` uses unsafe high-throughput pragmas for bulk migration inserts. `Close` closes all folder DBs then the main DB. `initTmpDir` sets `SQLITE_TMPDIR` on non-Windows/non-Darwin systems when unset.

## State and Persistence Behavior
The main database lives at `main.db` under the supplied directory; folder databases live next to it and are tracked from the main `folders` table. Opening can mutate state by creating directories, initializing schemas, cleaning orphaned folder files, and migrating folder DBs.

## Dependencies and Integration Points
The file integrates with `openBase`, SQL schema assets, `db.DB`, `folderDB`, `slog`, and `build` OS flags. `Open` is the entry point for almost every test in this subset.

## Risks and Test Signals
Risks include accidentally running migration pragmas in normal operation, temp-dir setup after SQLite initialization, and partial folder DB open failure after the main DB opens. `db_test.go` includes path-special-character coverage.
