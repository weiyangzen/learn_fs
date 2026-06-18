# sources/sync-backup/syncthing/internal/db/sqlite/db_update.go

## Purpose
This file implements top-level database update and housekeeping methods that operate around folder database lifecycle rather than individual file rows.

## Important APIs and Control Flow
`DropFolder` locks the folder map and main update lock, deletes the folder row from the main `folders` table, closes and removes the open folder DB file plus WAL/SHM side files, and removes it from the cache. `ListFolders` reads folder IDs ordered by ID. `cleanDroppedFolders` compares on-disk `folder.*` files with `folders.database_name` values and removes orphaned files. `startFolderDatabases` opens all listed folders to apply migrations. `wrap` annotates errors with the caller function name and optional context strings.

## State and Persistence Behavior
`DropFolder` mutates both the main DB and filesystem. `cleanDroppedFolders` can delete files during startup if their basename does not match any live database name prefix. `startFolderDatabases` may migrate or initialize folder DBs as a side effect.

## Dependencies and Integration Points
The file uses `os`, `filepath`, `slices`, `strings`, logging helpers, and the folder DB cache initialized in `db_open.go`. `wrap` is used throughout the SQLite package.

## Risks and Test Signals
Filesystem deletion is the main risk, especially name-prefix matching and WAL/SHM cleanup. `db_test.go` covers `DropFolder` behavior and `TestErrorWrap`; startup cleanup has less direct coverage.
