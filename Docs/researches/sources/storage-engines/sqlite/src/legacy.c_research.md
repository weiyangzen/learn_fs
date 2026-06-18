# sources/storage-engines/sqlite/src/legacy.c

## Purpose

`legacy.c` implements `sqlite3_exec()`, SQLite's legacy convenience API for executing one or more semicolon-separated SQL statements with an optional row callback. It is intentionally thin over the prepared-statement engine: prepare each statement, step it to completion, invoke the caller's callback for result rows, finalize, then continue with the remaining SQL tail.

## Important APIs, Types, and Functions

- `sqlite3_exec(sqlite3 *db, const char *zSql, sqlite3_callback xCallback, void *pArg, char **pzErrMsg)` is the only function in this file.
- It uses `sqlite3_prepare_v2()` to compile each statement and `sqlite3_step()` to execute it.
- It uses `sqlite3_column_count()`, `sqlite3_column_name()`, `sqlite3_column_text()`, and `sqlite3_column_type()` to prepare callback metadata and row values.
- It finalizes statements with `sqlite3VdbeFinalize()` rather than the public wrapper, because this is core code operating on the internal `Vdbe`.
- It reports connection-level status through `sqlite3Error()`, `sqlite3ApiExit()`, `sqlite3_errmsg()`, and `sqlite3DbStrDup()`.

## Control Flow

The routine first validates the database handle with `sqlite3SafetyCheckOk()`, treats a NULL SQL string as an empty string, enters the database mutex, and clears the connection error state. It then loops while the current SQL pointer is non-empty and no error has occurred.

Each iteration prepares the next statement and receives `zLeftover`, the tail after that statement. If preparation returns no statement, the input was whitespace or a comment, so it advances to `zLeftover`. Otherwise it steps the statement until completion.

Callback setup is lazy. On the first result row, or on `SQLITE_DONE` when `SQLITE_NullCallback` is set and no row has been seen, it allocates one array large enough for column names plus values and a trailing NULL. Column names are filled once. For each `SQLITE_ROW`, it fills the value half with text pointers and calls `xCallback(pArg, nCol, azVals, azCols)`.

If the callback returns non-zero, `sqlite3_exec()` aborts the statement, sets `SQLITE_ABORT`, finalizes immediately, and exits. When stepping returns anything other than `SQLITE_ROW`, it finalizes, advances to the leftover SQL, skips whitespace, frees callback column storage, and proceeds to the next statement.

On exit, any active statement and column storage are finalized/freed. The return code passes through `sqlite3ApiExit()`. If the final code is not `SQLITE_OK` and `pzErrMsg` is supplied, it duplicates `sqlite3_errmsg(db)` using the non-connection allocator so the caller can free it. On success, `*pzErrMsg` is set to NULL.

## State and Persistence Behavior

`sqlite3_exec()` does not add persistent state beyond whatever the SQL statements themselves do. It temporarily holds the connection mutex, temporarily allocates callback metadata from the database allocator, and may set the connection error state. Statements are finalized before return unless a severe internal path interrupts normal flow.

The callback receives pointers owned by the current statement for values and names; they are not persistent beyond the callback call/statement lifetime. When a non-NULL, non-text column cannot provide text, the routine treats that as OOM by calling `sqlite3OomFault(db)`.

## Dependencies and Integration Points

This file includes `sqliteInt.h` and depends on the VDBE, prepare, column, mutex, allocator, error, and safety-check internals. The extension API table in `loadext.c` exports `sqlite3_exec` to loadable extensions. Many internal and test utilities call this convenience API when they do not need manual statement control; examples appear in `analyze.c`, `table.c`, `prepare.c`, `vdbe.c`, the shell, TCL bindings, and tests.

The callback contract is part of the public C API, and this implementation preserves documented behavior such as aborting with `SQLITE_ABORT` when the callback returns non-zero and invoking the callback once with NULL values for empty result sets when `SQLITE_NullCallback` is enabled.

## Risks and Edge Cases

The main risk is callback lifetime and reentrancy. The function holds the connection mutex while invoking user code, so callbacks that interact with the same connection must rely on SQLite's supported mutex/reentrancy semantics. Callback-provided pointers must not be retained by callers.

Error handling must preserve the first meaningful failing code while still finalizing statements. OOM can happen while allocating the column-name/value array or duplicating the final error string; the latter converts the return to `SQLITE_NOMEM_BKPT`.

Multi-statement parsing depends on `sqlite3_prepare_v2()` setting `zLeftover` correctly. Whitespace/comment-only input must not loop forever. The `SQLITE_NullCallback` path is subtle because it can invoke the callback on `SQLITE_DONE` without row values.

## Test Signals

Relevant test signals include public C API tests in `src/test1.c` wrappers (`sqlite3_exec`, `sqlite3_exec_nr`, hex/printf variants), `test/capi3d.test` callback/reentrancy cases, bad UTF/OOM tests, and any test using `sqlite3_get_table()` because `table.c` builds on `sqlite3_exec()`.

Focused regression tests should cover multiple statements, whitespace/comment-only SQL, callback abort, NULL `zSql`, NULL callback, `SQLITE_NullCallback`, OOM during callback metadata allocation, error message allocation failure, and statements that produce zero columns versus result rows.
