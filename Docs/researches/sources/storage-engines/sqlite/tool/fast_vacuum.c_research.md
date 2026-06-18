# sources/storage-engines/sqlite/tool/fast_vacuum.c

## Purpose
`fast_vacuum.c` demonstrates a high-speed alternative to SQLite `VACUUM` that copies schema and table content into a temporary attached database, then renames files. It is explicitly demonstration code with operational restrictions.

## Important APIs, Types, and Functions
`vacuumFinalize()` finalizes statements and exits on errors. `execSql()` prepares, prints, steps, and finalizes one SQL statement. `execExecSql()` runs a query that returns SQL text and executes each returned statement. `main()` opens the database, generates random temp/backup names, attaches the temp database, copies schema/content, commits, closes, and renames files.

## Control Flow
After validating one database argument, the program opens the database, builds random names ending in `-vacuum-...` and `-backup-...`, attaches the temp DB as `vacuum_db`, enables `writable_schema`, begins a transaction, creates mirror tables and indexes by transforming `sqlite_schema.sql`, copies table rows, handles `sqlite_sequence`, inserts view/trigger/virtual-table schema rows directly, commits, closes, renames the original to backup, and renames the temp database to the original name.

## State and Persistence
It creates a new temporary database file, creates a backup name for the original, and ultimately replaces the original database path. The original database remains under the backup name if renames succeed. It does not use SQLite's normal `VACUUM` machinery.

## Dependencies and Integration Points
It depends on `sqlite3.h`, `sqlite3.c` at link time, C runtime file rename behavior, and SQLite schema table format. It is a sample for developers and a test utility for vacuum-like copying.

## Risks
The comments identify major risks: callers must ensure exclusive external access; page-size and auto-vacuum changes are unsupported; crashes during rename can leave unexpected filenames. Additional risks include fragile SQL string slicing for schema recreation, limited support for newer schema objects, direct `writable_schema` writes, no checking of `rename()` results, and possible leftover temp/backup files.

## Test Signals
Use disposable databases with tables, indexes, unique indexes, views, triggers, virtual tables, and `sqlite_sequence`; compare content before and after with `dbhash`; verify file size reduction; test interrupted runs manually in a sandbox; confirm concurrent access is not allowed by policy rather than code.
