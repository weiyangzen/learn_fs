# sources/storage-engines/sqlite/tool/rollback-test.c

## Purpose

Utility for creating and checking databases with hot journals, especially across machines with different architectures. It can create a deterministic test database, intentionally exit mid-transaction to leave rollback or WAL recovery state, and later verify that recovery restores correct content.

## Important APIs, control flow, and dependencies

The program links SQLite directly through `sqlite3.h`. `openDb()` opens a database and exits on failure. `execCallback()` accumulates result text in the global `zReply`, and `runSql()` executes SQL and surfaces SQLite errors. `main()` supports `new`, `check`, and `crash`: `new` accepts encoding and page-size options, creates table `t1`, expands it to 1024 rows, updates text values, and creates an index; `check` runs `PRAGMA integrity_check` and verifies all values; `crash` optionally switches journal mode to WAL or DELETE, starts a transaction, updates all rows, and exits without closing/committing.

## State, persistence, and integration

This is deliberately stateful: it creates database content and can leave hot rollback journal or WAL state on disk by terminating abruptly. The `check` command relies on SQLite opening the database and performing normal recovery before running validation SQL. Options let tests vary text encoding, page size, and journal mode.

## Risks and test signals

Risks are intentional: abrupt `exit(0)` can leave files that depend on OS flush semantics, filesystem behavior, and SQLite journaling mode. The fixed-size reply buffer can truncate unexpected query output, though normal checks are small. Test signals are `Ok` from `check`, integrity_check output, row-content validation after moving files across architectures, and separate runs for rollback and WAL journal modes.
