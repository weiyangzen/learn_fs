# sources/storage-engines/sqlite/ext/wasm/demo-123.js

## Purpose

`demo-123.js` is a basic demonstration of SQLite's WASM OO API #1. It can run in the main browser thread or a worker thread and shows database creation, SQL execution, prepared statements, result row modes, scalar UDF registration, transactions, savepoints, and explicit cleanup.

## Important APIs, Types, and Functions

- `logHtml()`, `log()`, `warn()`, and `error()`: output abstraction. The main thread writes DOM nodes; the worker posts `type: "log"` messages.
- `demo1(sqlite3)`: main demonstration routine.
- `sqlite3.capi`: C-style API access, used for version/source ID output.
- `sqlite3.oo1.DB`: high-level database wrapper. The demo opens `new oo.DB("/mydb.sqlite3", "ct")`.
- `db.exec()`: demonstrated with SQL strings, option objects, bind arrays, named bind objects, callbacks, `resultRows`, `columnNames`, and multiple row modes.
- `db.prepare()`, `Stmt.bind()`, `Stmt.step()`, `Stmt.reset()`, `Stmt.stepReset()`, and `Stmt.finalize()`.
- `db.createFunction()`: registers a scalar UDF named `twice`.
- `db.transaction()` and `db.savepoint()`: demonstrate rollback through thrown `sqlite3.SQLite3Error`.

## Control Flow

The script first detects whether it is running on the window or worker global object and installs the correct logging path. In worker mode it may import `sqlite3.js` after honoring a `sqlite3.dir` query parameter. It calls `sqlite3InitModule({print, printErr})`, then executes `demo1(sqlite3)` once initialization resolves.

Inside `demo1()`, the code opens a transient database, creates a table, inserts rows through `exec()` and a prepared statement, queries through all supported row modes, collects results without a callback, creates and exercises a UDF, checks expected UDF argument-count failure, demonstrates transaction rollback, demonstrates nested savepoint rollback, and closes the database in `finally`.

## State and Persistence

The database filename is `/mydb.sqlite3` with flags `"ct"`, meaning a create/truncate style transient database in the active VFS. It is closed at the end. Prepared statement lifetime is explicitly managed with `try/finally` and `finalize()`. The script intentionally warns users not to rely on garbage collection for DB or statement cleanup.

## Dependencies and Integration Points

The script requires `sqlite3InitModule` and the SQLite WASM build. In the main thread it expects DOM access for logging; in worker mode it expects the embedding page to handle posted log messages. It integrates with Emscripten-style `print` and `printErr` module options for stdout/stderr routing.

## Risks and Edge Cases

- If run in a worker from a different directory than `sqlite3.js`, callers must pass `sqlite3.dir` or WASM resolution can fail.
- Errors in the expected rollback/UDF-failure paths are swallowed only if they are `sqlite3.SQLite3Error`; other exceptions are rethrown.
- The demo is not a persistence test. The database is closed and intended as transient demonstration state.
- DOM logging assumes `document.body` exists in main-thread mode.

## Test Signals

The demo's own observable signals are successful log output for version, inserts, query rows in each row mode, expected UDF arity exception, expected transaction rollback count, expected nested savepoint rollback count, and final close without leaked statements. A harness can run it in both main-thread and worker modes to verify loader and logging paths.
