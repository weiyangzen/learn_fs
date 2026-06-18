<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_backup.c -->
# sources/storage-engines/sqlite/src/test_backup.c

## Purpose
`test_backup.c` wraps the incremental backup API in Tcl. It creates a Tcl command representing a live `sqlite3_backup*` handle so scripts can step, inspect, and finish backups explicitly.

## Important APIs, Types, and Functions
The main command `sqlite3_backup` is registered by `Sqlitetestbackup_Init()`. `backupTestInit()` calls `sqlite3_backup_init()` and creates a per-backup Tcl command handled by `backupTestCmd()`. Subcommands are `step npage`, `finish`, `remaining`, and `pagecount`. Cleanup uses `backupTestFinish()` as the Tcl command delete proc. It depends on `getDbPointer()` and `sqlite3ErrName()`.

## Control Flow
`sqlite3_backup CMDNAME DESTHANDLE DESTNAME SRCHANDLE SRCNAME` resolves Tcl database handles to `sqlite3*`, starts the backup, and registers `CMDNAME` with the backup pointer as client data. The `step` subcommand parses a page count and returns the symbolic result of `sqlite3_backup_step()`. `finish` removes the Tcl command's delete proc, deletes the command, calls `sqlite3_backup_finish()`, and returns the symbolic result. Query subcommands return `sqlite3_backup_remaining()` and `sqlite3_backup_pagecount()`.

## State and Persistence Behavior
The live backup object is owned by the generated Tcl command. If the command is deleted without explicit `finish`, `backupTestFinish()` finalizes it. Backup operations move pages from the source database to the destination database according to SQLite's backup API and may persist changes in destination files.

## Dependencies and Integration Points
This file integrates with Tcl SQLite database command handles, public backup APIs, Tcl command lifecycle hooks, and symbolic error names. It supports tests that need to interleave backup steps with writes, locks, or schema changes.

## Risks
The initializer does not check return values from `getDbPointer()` before using the output pointers. The `finish` path carefully disables the delete proc before deleting the Tcl command to avoid double finish; changes there would risk use-after-free. A failed `sqlite3_backup_init()` reports a generic message rather than the destination connection error.

## Test Signals
Signals include `SQLITE_OK`, `SQLITE_DONE`, `SQLITE_BUSY`, or other symbolic step/finish results, changing remaining/pagecount values, and automatic cleanup if the Tcl command is deleted.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_backup.c -->
