# sources/storage-engines/sqlite/ext/intck/test_intck.c

## Purpose
`test_intck.c` exposes the incremental integrity-check API to SQLite's Tcl test harness. It provides object-style Tcl commands for stepwise checks and a convenience command for full checks.

## Important APIs, Types, And Functions
`Sqlitetestintck_Init()` registers `sqlite3_intck` and `test_do_intck`. `TestIntck` stores one `sqlite3_intck *`. `test_sqlite3_intck()` opens a checker and creates a unique Tcl command. `testIntckCmd()` implements `close`, `step`, `message`, `error`, `unlock`, and `test_sql`. `test_do_intck()` runs a full check and returns messages as a Tcl list. `testIntckFree()` closes handles on command deletion.

## Control Flow
`sqlite3_intck DB DBNAME` resolves the SQLite pointer, maps empty database name to default NULL, opens the checker, creates `intckN`, and returns its name. Subcommands call the C API and convert return codes. `test_do_intck` opens, steps until done/error, appends non-empty messages, checks final error state, closes, and returns either the list or an error.

## State And Persistence
State is limited to the Tcl command client data and the wrapped `sqlite3_intck` handle. No database writes are performed by this wrapper.

## Dependencies And Integration Points
It depends on `sqlite3.h`, `sqlite3intck.h`, `tclsqlite.h`, Tcl APIs, and SQLite test helpers `getDbPointer()` and `sqlite3ErrName()`.

## Risks
If `getDbPointer()` fails after allocation, `TestIntck` is leaked. The `error` subcommand may pass NULL to `Tcl_NewStringObj()` when no error message exists. The wrapper inherits the production API's same-handle usage restriction.

## Test Signals
Cover command lifecycle, all subcommands, automatic cleanup, unlock/resume, `test_sql`, full-run message collection, open failures, and error propagation.
