# sources/storage-engines/sqlite/ext/misc/stmt.c

## Purpose
Implements the `sqlite_stmt` eponymous virtual table, exposing all prepared statements on the current database connection along with statement status counters and metadata.

## Important APIs, Types, And Functions
Important types are `StmtRow`, `stmt_vtab`, and `stmt_cursor`. Module methods include `stmtConnect`, `stmtOpen`, `stmtFilter`, `stmtNext`, `stmtColumn`, `stmtRowid`, `stmtEof`, `stmtClose`, and `stmtBestIndex`. Public initialization is through `sqlite3StmtVtabInit()` and, when built as an extension, `sqlite3_stmt_init()`.

## Control Flow
`stmtConnect()` declares columns `sql,ncol,ro,busy,nscan,nsort,naidx,nstep,reprep,run,mem` and stores the connection handle. `stmtFilter()` resets cursor-owned rows, walks `sqlite3_next_stmt()`, copies SQL text and status counters into a linked list of `StmtRow` objects, and assigns rowids. Cursor advancement frees the current row and moves to `pNext`; columns read from the snapshot row.

## State And Persistence Behavior
No persistent database state is changed. Cursor state is a snapshot linked list allocated during `xFilter`; the virtual table object stores only the database handle. Statement counters are read without reset by passing `0` to `sqlite3_stmt_status()`.

## Dependencies And Integration Points
Depends on SQLite virtual table support and introspection APIs: `sqlite3_next_stmt`, `sqlite3_sql`, `sqlite3_column_count`, `sqlite3_stmt_readonly`, `sqlite3_stmt_busy`, and `sqlite3_stmt_status`. It is conditionally compiled for core builds with `SQLITE_ENABLE_STMTVTAB` and omitted if virtual tables are disabled.

## Risks And Edge Cases
The snapshot may include the statement currently running the query. Memory use scales with the number and SQL text size of prepared statements. The table is read-only and planner estimates are fixed. If prepared statements are finalized after snapshot creation, copied SQL text and counters remain safe because rows are independent copies.

## Test Signals
Tests should prepare several statements, run some to change counters, query `sqlite_stmt`, verify SQL text, busy/read-only flags, rowid sequence, status counters, no-reset behavior, and clean operation when no other statements exist.
