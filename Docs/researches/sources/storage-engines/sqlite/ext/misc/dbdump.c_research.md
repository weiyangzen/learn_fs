# sources/storage-engines/sqlite/ext/misc/dbdump.c

## Purpose

`dbdump.c` implements `sqlite3_db_dump()`, a C API that emits UTF-8 SQL text able to recreate a database schema and contents while preserving rowid values when needed. With `DBDUMP_STANDALONE`, it also builds a command-line utility around that API.

## Important APIs, types, and functions

The exported API is `sqlite3_db_dump(sqlite3 *db, const char *zSchema, const char *zTable, int (*xCallback)(const char*,void*), void *pArg)`. `DState` tracks the connection, error count, return code, writable-schema state, and output callback. `DText` is a growable string helper used to build SQL fragments.

`tableColumnList()` discovers table columns via `PRAGMA table_info`, detects integer primary key and rowid preservation needs, and avoids inaccessible rowid aliases. `dump_callback()` emits table DDL and `INSERT` statements. `output_quoted_escaped_string()` safely emits SQL string literals, preserving newline and carriage-return bytes using nested `replace()` expressions. `output_sql_from_query()` emits indexes, triggers, and views from schema queries.

## Control flow

`sqlite3_db_dump()` starts a transaction on the source database, emits `PRAGMA foreign_keys=OFF; BEGIN TRANSACTION;`, then either dumps all tables or a single named table. Table rows are selected through generated `SELECT` statements and emitted according to SQLite type: integers, floats, NULLs, quoted text, and hex blobs. Virtual table DDL is recreated by inserting its schema row under `PRAGMA writable_schema=ON` rather than executing `CREATE VIRTUAL TABLE`. After schema objects are emitted, writable-schema mode is disabled if used, and the output ends in `COMMIT` or `ROLLBACK` based on error count.

## State and persistence

The function reads the supplied database and writes only to the callback. It opens and commits a read transaction around the dump to stabilize source reads. It does not modify database contents, except for transaction state on the connection used for dumping. Standalone mode opens a database path and writes to stdout.

## Dependencies and integration points

It depends on core SQLite C APIs, schema tables, pragmas, keyword checks, `sqlite3_table_column_metadata()`, and callback-style streaming output. It is intended to mirror shell `.dump` behavior in embeddable form.

## Risks

Dump correctness is sensitive to rowid alias detection, WITHOUT ROWID handling, quoted identifiers, virtual table handling, and floating-point special values. Callback failures are not strongly propagated because the callback return value is not consistently checked by helper functions. The code emits schema queries against `sqlite_schema` in some places and the requested schema in others, so attached-schema dumping should be tested carefully. Memory allocation failure in `DText` can suppress later output by clearing the buffer.

## Test signals

Coverage should recreate databases containing rowid tables, INTEGER PRIMARY KEY tables, WITHOUT ROWID tables, hidden rowid-name collisions, blobs, embedded quotes/newlines/CR text, infinities, indexes, triggers, views, virtual tables, `sqlite_sequence`, sqlite_stat tables, single-table dumps, attached schemas, and standalone CLI argument errors.
