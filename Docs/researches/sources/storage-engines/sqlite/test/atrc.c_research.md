# sources/storage-engines/sqlite/test/atrc.c

## Purpose
`atrc.c` is a standalone utility that generates a SQLite CLI script to stress `ALTER TABLE ... RENAME` handling. It opens an existing database, discovers user tables and columns, emits SQL to rename every column and table to synthetic names, runs schema and integrity checks, then emits undo SQL and rolls back the transaction.

## Important APIs, Types, and Functions
- `rename_all_columns_of_table()` prepares `SELECT name FROM pragma_table_info(?1)`, binds a table name, and appends quoted `ALTER TABLE ... RENAME COLUMN` statements to `sqlite3_str` accumulators.
- `rename_all_tables()` scans `sqlite_schema` for non-internal tables, generates new table names (`txN`) and column prefixes, calls column rename generation, and appends table rename/undo statements.
- `main()` opens the target database, builds forward and reverse SQL with `sqlite3_str_new()`/`sqlite3_str_finish()`, closes the connection, and prints a CLI script.

## Control Flow
The program requires one database argument. It builds conversion SQL and undo SQL from live schema introspection, then prints `BEGIN;`, all rename operations, `.schema --indent`, `PRAGMA integrity_check;`, undo operations, another integrity check, and `ROLLBACK;`.

## State and Persistence Behavior
The utility reads schema metadata from the supplied database but does not apply changes itself. The generated script wraps all ALTER TABLE operations in a transaction that ends with `ROLLBACK`, so intended persistent database state is unchanged. The printed CLI script can still exercise real schema rewrite code, generated columns, triggers, indexes, views, and foreign keys while the transaction is active.

## Dependencies and Integration Points
It depends on public `sqlite3.h`, `sqlite3_prepare_v2`, `sqlite3_bind_text`, `sqlite3_step`, `sqlite3_column_text`, `sqlite3_str`, and SQLite `%w` identifier quoting in `sqlite3_str_appendf()`. It is designed to be piped into the SQLite shell, so `.schema --indent` is a CLI command rather than SQL.

## Risks and Edge Cases
The code ignores return codes from the recursive column/table rename calls after initial prepare success, so allocation or schema-query errors may produce partial scripts. The undo table rename uses `%s` for generated names and `%w` for original names; generated names are controlled (`txN`), but any future change should preserve identifier quoting. It only targets the `main` schema and skips `sqlite_%` tables.

## Test Signals
Success is a generated script that runs without ALTER TABLE errors and returns clean `PRAGMA integrity_check` results before rollback. The `.schema --indent` output offers a human-readable signal that dependent SQL text survived renames.
