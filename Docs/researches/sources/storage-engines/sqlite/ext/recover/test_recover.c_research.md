# sources/storage-engines/sqlite/ext/recover/test_recover.c

## Purpose

`test_recover.c` is the SQLite Tcl test harness binding for the recover extension and the related `sqlite_dbdata` registration hook. It lets Tcl tests create a `sqlite3_recover` handle, configure it, step or run it, inspect errors, finalize it, and test SQL-callback mode without writing C test code for each scenario.

## Important APIs, Types, and Functions

`TestRecover` stores the active `sqlite3_recover *`, the Tcl interpreter, and an optional callback script object used by SQL-emitting recovery. `xSqlCallback()` duplicates the configured Tcl script, appends the emitted SQL statement, evaluates it, and converts an empty result to `SQLITE_OK` or a numeric result to the callback return code. `getDbPointer()` resolves a Tcl SQLite command name to its underlying `sqlite3 *` via command client data.

`test_sqlite3_recover_init()` implements both `sqlite3_recover_init DB DBNAME URI` and `sqlite3_recover_init_sql DB DBNAME SCRIPT`, distinguished by `clientData`. It allocates `TestRecover`, creates the underlying recover handle, assigns a generated Tcl command name such as `sqlite_recover1`, and registers `testRecoverCmd()` as the object command.

`testRecoverCmd()` implements subcommands `config`, `run`, `errmsg`, `errcode`, `finish`, and `step`. Config options map Tcl names to recover opcodes: `testdb` uses the undocumented implementation opcode `789`, `lostandfound` maps to `SQLITE_RECOVER_LOST_AND_FOUND`, `freelistcorrupt` to `SQLITE_RECOVER_FREELIST_CORRUPT`, `rowids` to `SQLITE_RECOVER_ROWIDS`, `slowindexes` to `SQLITE_RECOVER_SLOWINDEXES`, and `invalid` deliberately sends an unknown opcode. `test_sqlite3_dbdata_init()` registers `sqlite_dbdata`/`sqlite_dbptr` against a Tcl database handle. `TestRecover_Init()` installs the top-level Tcl commands.

## Control Flow

Tests call `sqlite3_recover_init` or `sqlite3_recover_init_sql` with a Tcl DB handle and database name. The returned Tcl command wraps one C recover handle. A typical test then invokes `$R config ...`, `$R run` or repeated `$R step`, `$R errcode`/`$R errmsg`, and `$R finish`.

In SQL-callback mode, every SQL statement emitted by `sqlite3recover.c` re-enters Tcl through `xSqlCallback()`. The script receives the statement as an appended argument, so tests can collect SQL text, replay it into another database, inject callback errors, or filter for specific statements such as lost-and-found inserts. If Tcl evaluation fails or returns a non-integer non-empty result, `Tcl_BackgroundError()` is used and the recover callback reports `TCL_ERROR`.

## State and Persistence Behavior

The wrapper keeps the C recover handle alive until the Tcl subcommand `finish` is called. `finish` first checks `sqlite3_recover_errcode()`, exposes the error message as the Tcl result if non-OK, calls `sqlite3_recover_finish()`, asserts the returned code matches the prior error code, and returns a Tcl error when recovery failed. SQL callback scripts are refcounted with `Tcl_IncrRefCount()` when the handle is created, but this file does not define a Tcl command delete callback to release `TestRecover` if a command is deleted without `finish`.

The output database or SQL replay persistence is controlled by the underlying recover implementation. This shim itself persists no database state except by invoking recover APIs and optional `sqlite3_dbdata_init()`.

## Dependencies and Integration Points

The file includes `sqlite3recover.h`, `sqliteInt.h`, and `tclsqlite.h`, so it is part of SQLite's internal test build rather than a standalone public extension. It depends on the Tcl command representation used by the SQLite test harness, where `objClientData` points at a `sqlite3 *`. It also declares `sqlite3_dbdata_init()` so tests can load dbdata virtual tables independently.

## Risks and Edge Cases

The wrapper is intentionally thin and test-oriented. It does not validate that `sqlite3_recover_init()` returned non-NULL before registering a Tcl command, so OOM paths depend on subsequent recover APIs returning `SQLITE_NOMEM` for null handles or on tests not dereferencing invalid wrapper state. The absence of a command deletion callback means abnormal Tcl command deletion can leak the `TestRecover` allocation and retained callback script. The `testdb` option uses a magic opcode that is explicitly implementation-private.

Callback result conversion is another risk: an empty Tcl result means success, an integer result is passed through to recover, and non-integer text becomes a Tcl background error. This is useful for fault injection but can mask script mistakes as callback failures.

## Test Signals

This file is exercised by the recover Tcl suites under `ext/recover`. Signals include successful command creation, exact SQLite integer return codes from `config`, `run`, and `step`, error message propagation through `finish`, callback SQL collection in `recover1.test`, `recoverold.test`, and `recoversql.test`, invalid config opcode coverage, and independent `sqlite3_dbdata_init` setup for low-level dbdata tests.
