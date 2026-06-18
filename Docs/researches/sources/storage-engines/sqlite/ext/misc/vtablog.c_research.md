# Research: sources/storage-engines/sqlite/ext/misc/vtablog.c

## Purpose

`vtablog.c` implements a loadable virtual table module named `vtablog` that prints diagnostic messages to stdout whenever SQLite calls key virtual-table methods. It is an interactive teaching and debugging aid for understanding SQLite's virtual table planning, scanning, update, transaction, rename, shadow-name, and integrity callbacks.

The virtual table returns synthetic rows. Its behavior can be configured at `CREATE VIRTUAL TABLE` time with a declared schema, row count, and optional `ORDER BY` consumption rule.

## Important APIs, Types, And Functions

- `sqlite3_vtablog_init()` registers the `vtablog` module.
- `vtablog_vtab` stores schema/table names, configured row count, cursor counter, and `consume_order_by` setting.
- `vtablog_cursor` stores a cursor identifier and current rowid.
- `vtablogConnectCreate()` handles both `xCreate` and `xConnect`, prints argv details, parses `schema=`, `rows=`, and `consume_order_by=`, declares the requested schema, and initializes table state.
- `vtablogBestIndex()` prints `colUsed`, constraints, RHS values from `sqlite3_vtab_rhs_value`, collations from `sqlite3_vtab_collation`, order-by terms, `sqlite3_vtab_distinct`, and chosen estimates. It may set `orderByConsumed`.
- `vtablogFilter`, `vtablogNext`, `vtablogEof`, `vtablogColumn`, and `vtablogRowid` implement a simple rowid scan from 0 to `nRow-1` while printing each callback.
- `vtablogUpdate` prints INSERT/UPDATE/DELETE arguments but does not change table content.
- Transaction methods (`xBegin`, `xSync`, `xCommit`, `xRollback`, savepoint methods), `xFindMethod`, `xRename`, `xShadowName`, and `xIntegrity` are implemented for observability.

## Control Flow

Creating or connecting prints module arguments and parses options from arguments 3 onward. If no schema is supplied, it declares `CREATE TABLE x(a,b);`. The table object stores `argv[1]` and `argv[2]` as display names and defaults to ten rows.

Planning prints all constraint/order metadata and assigns a fixed estimated cost and row count. If `consume_order_by=N` was configured and the first order-by term matches column `N-1` ascending, or `-N` descending, `orderByConsumed` is set.

Scanning allocates a cursor with a unique display id, initializes rowid to zero on `xFilter`, increments on `xNext`, reports EOF when `iRowid >= nRow`, returns generated text values for each column, and returns rowid equal to `iRowid`. Updates and transaction callbacks only log invocation.

## State And Persistence Behavior

The module has no durable storage. `nRow`, `iConsumeOB`, and display names live in each virtual-table object. `nCursor` monotonically increases for the table object's lifetime. Rows are generated on demand and all writes are no-ops that return success. `xRename` updates only the in-memory display name used in later log messages.

All diagnostic output goes to stdout through `printf`, so callers must manage stdout capture if using it in automated tests.

## Dependencies And Integration Points

The file uses the SQLite loadable-extension ABI and virtual-table API version 4, including newer callbacks such as `xShadowName` and `xIntegrity`, and planner helpers `sqlite3_vtab_rhs_value`, `sqlite3_vtab_collation`, and `sqlite3_vtab_distinct`. It depends on standard C stdio, string, ctype, assert, and stdlib.

## Risks And Edge Cases

- `vtablog_trim_whitespace()` checks `z[n]` instead of `z[n-1]` in its loop, so trailing whitespace trimming is ineffective for the last real character.
- Output is synchronous stdout logging with no mutexing or structured log sink.
- `vtablogColumn` uses the string `"abcdefghijklmnopqrstuvwyz"`, which omits `x`; generated labels are only diagnostic.
- `xUpdate` reports success without modifying any state, which can surprise users treating it as a real writable table.
- `xBestIndex` does not use constraints to improve scans; it only demonstrates planner metadata.
- `xShadowName` classifies any name containing `"shadow"` as a shadow table, purely for testing interface behavior.

## Test Signals

Useful tests load the extension, create a table with custom schema/row count, run SELECTs with constraints, collations, RHS constants, order-by terms, updates, transactions, savepoints, rename, integrity checks, and table names containing `"shadow"`. Expected stdout should show method order and planner metadata. Result tests should verify generated rows and `orderByConsumed` behavior when configured.
