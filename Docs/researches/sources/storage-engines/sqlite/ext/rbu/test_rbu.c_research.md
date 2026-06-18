# sources/storage-engines/sqlite/ext/rbu/test_rbu.c

## Purpose

`test_rbu.c` is the SQLite test harness glue for the RBU extension. When compiled with `SQLITE_TEST` and RBU support, it registers Tcl commands that construct RBU handles, expose handle methods, create or destroy RBU VFS instances, and run small internal tests. It lets the Tcl test suite exercise the C API, observe return codes, inject rename failures, register a Tcl-backed `rbu_delta()` SQL function, and inspect progress/temp-space behavior.

## Important APIs, Types, and Functions

`TestRbu` binds a `sqlite3rbu *`, a `Tcl_Interp *`, and an optional Tcl rename script. `test_rbu_delta()` implements a SQL function that calls the Tcl command `rbu_delta` with the SQL arguments and returns the Tcl result as text. `xRenameCallback()` adapts a Tcl script to the `sqlite3rbu_rename_handler()` callback signature.

`test_sqlite3rbu_cmd()` is the per-handle Tcl object command. It supports `step`, `close`, `close_no_error`, `create_rbu_delta`, `savestate`, `dbMain_eval`, `dbRbu_eval`, `bp_progress`, `db`, `state`, `progress`, `temp_size_limit`, `temp_size`, and `rename_handler`. `createRbuWrapper()` allocates `TestRbu` and registers this object command for a new handle.

Top-level Tcl commands are implemented by `test_sqlite3rbu()` (`sqlite3rbu NAME TARGET-DB RBU-DB ?STATE-DB?`), `test_sqlite3rbu_vacuum()` (`sqlite3rbu_vacuum NAME TARGET-DB ?STATE-DB?`), `test_sqlite3rbu_create_vfs()`, `test_sqlite3rbu_destroy_vfs()`, and `test_sqlite3rbu_internal_test()`. `SqliteRbu_Init()` registers them with the Tcl interpreter.

## Control Flow

Tests create a handle command by invoking `sqlite3rbu` or `sqlite3rbu_vacuum`. The wrapper immediately calls `sqlite3rbu_open()` or `sqlite3rbu_vacuum()`, stores the handle in `TestRbu`, and returns the Tcl command name. Tests then drive the object command one method at a time. `step` returns a symbolic SQLite error name via `sqlite3ErrName()`. `close` deletes the Tcl command first, calls `sqlite3rbu_close()`, reports the result and optional error message, decrements any rename script reference, and frees the wrapper.

The `create_rbu_delta` method obtains the target database handle through `sqlite3rbu_db(pRbu, 0)` and registers `test_rbu_delta()` as `rbu_delta`. The `dbMain_eval` and `dbRbu_eval` methods execute SQL directly against the corresponding internal handle. The `db` method returns a pointer string for lower-level Tcl tests. The `rename_handler` method either restores default rename handling with an empty script or duplicates a Tcl script and registers `xRenameCallback()`.

`sqlite3rbu_create_vfs ?-default? NAME PARENT` calls the public VFS constructor and optionally registers the new VFS as default. `sqlite3rbu_destroy_vfs NAME` calls the public destructor. If RBU is not compiled in, `SqliteRbu_Init()` is a no-op that returns `TCL_OK`.

## State and Persistence Behavior

The harness owns wrapper lifetime, not RBU persistence. It frees `TestRbu` only during `close`/`close_no_error`; tests that do not close a command would leak the wrapper for the interpreter lifetime. Any persistent RBU state is stored by the implementation in the RBU or state database, and this harness exposes `savestate` and `close` to force those paths.

The optional rename script is reference-counted as a Tcl object. Registering a non-empty script stores a duplicate and increments its refcount; closing decrements it. The current implementation does not decrement a previous script when `rename_handler` is called repeatedly with a different non-empty script, so tests should avoid repeated replacement without close or be aware of the leak.

## Dependencies and Integration Points

This file depends on the SQLite test harness (`SQLITE_TEST`, `tclsqlite.h`, `sqlite3ErrName()`, `sqlite3TestMakePointerStr()`), Tcl APIs, and the RBU public header. It is not part of normal production builds unless the test configuration enables it. Its returned strings and method names are consumed by the Tcl tests under `sources/storage-engines/sqlite/ext/rbu`.

The harness is intentionally thin: it does not simulate RBU behavior, but delegates to the real public API. This makes it a reliable integration layer for testing VFS creation/destruction, progress APIs, state transitions, rename callbacks, temp-size accounting, and direct SQL interactions with RBU-owned database handles.

## Risks and Test Signals

Because Tcl scripts can execute arbitrary code during `rbu_delta` or rename callbacks, tests can create timing, error, and reentrancy scenarios that normal callers might not. `xRenameCallback()` maps any Tcl error to `SQLITE_IOERR`, which is useful for fault tests but loses detailed Tcl error information at the RBU layer. `dbMain_eval` and `dbRbu_eval` ignore result rows and only surface `sqlite3_exec()` errors, so they are best for setup/fault injection rather than query assertions.

The internal test checks only that `sqlite3rbu_db(0, 0)` returns NULL. Broader behavioral coverage comes from Tcl tests invoking this harness, especially tests for crash/resume, busy handling, rename failure, progress reporting, delta updates, temp-size limits, VFS stacking, and close error propagation.
