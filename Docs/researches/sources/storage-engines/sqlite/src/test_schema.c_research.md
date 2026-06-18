<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_schema.c -->
# sources/storage-engines/sqlite/src/test_schema.c

## Purpose
`test_schema.c` defines a read-only virtual table module named `schema` that exposes one row per column in all attached database schemas. It is used by SQLite tests and can also be built as a loadable extension outside `SQLITE_TEST`.

## Important APIs, Types, And Functions
The virtual table schema has columns `database`, `tablename`, `cid`, `name`, `type`, `not_null`, `dflt_value`, and `pk`. Types `schema_vtab` and `schema_cursor` hold the database handle and three nested statements. Virtual table methods include `schemaCreate()`, `schemaOpen()`, `schemaFilter()`, `schemaNext()`, `schemaColumn()`, `schemaRowid()`, and `schemaClose()`. Registration is via Tcl `register_schema_module` or extension entry point `sqlite3_schema_init()`.

## Control Flow
Filtering prepares `PRAGMA database_list` and immediately advances to the first column. `schemaNext()` walks a nested loop: databases from `database_list`, tables from each schema's `sqlite_schema` or `sqlite_temp_schema`, then columns from `PRAGMA <db>.table_info(<table>)`. `schemaColumn()` maps virtual table columns to the active database-list, table-list, or column-list statement. End-of-scan is represented by a null `pDbList`.

## State And Persistence Behavior
The module is read-only and persists no data. Cursor state is a set of prepared statements and a monotonically increasing rowid. Statements are finalized as each loop level is exhausted or when the cursor closes.

## Dependencies And Integration Points
It depends on virtual-table support, SQLite prepare/step/finalize APIs, `%Q` quoting through `sqlite3_mprintf()`, and Tcl helpers in test builds. Outside test builds it uses `sqlite3ext.h` and `SQLITE_EXTENSION_INIT`.

## Risks And Test Signals
Risks include schema changes while scanning, no constraint pushdown, errors during `schemaNext()` only surfaced as return codes, and memory allocation failures while building PRAGMA SQL. Test signals include rows for main, temp, and attached schemas; correct `table_info` column values; clean finalization on early close; loadable-extension registration; and no rows or harmless registration when virtual tables are omitted.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_schema.c -->
