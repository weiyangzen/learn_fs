# sources/storage-engines/sqlite/ext/rbu/rbu.c

## Purpose

`rbu.c` is a small command-line driver for SQLite's Resumable Bulk Update extension. It applies an RBU update database to a target database, or runs an RBU-backed vacuum, using the public `sqlite3rbu.h` API. It exists as an executable wrapper around the library, with options for bounded stepping, periodic memory/progress reporting, vacuum mode, and optional SQL run against the opened RBU connections before stepping.

## Important APIs And Functions

`usage(const char *zArgv0)` prints command syntax and exits with code 1. The supported options are `-step NSTEP`, `-statstep NSTATSTEP`, `-vacuum`, and `-presql SQL`, followed by `TARGET-DB RBU-DB`.

`report_default_vfs()` reports the process default VFS using `sqlite3_vfs_find(0)`. `report_rbu_vfs(sqlite3rbu *pRbu)` obtains the target database connection from `sqlite3rbu_db(pRbu, 0)`, asks SQLite for `SQLITE_FCNTL_VFSNAME` on schema `main`, prints the VFS name if available, and frees the returned name with `sqlite3_free()`.

`main()` parses options by allowing abbreviated option names through prefix `memcmp()` checks bounded by each option's full length. It opens either `sqlite3rbu_vacuum(zTarget, zRbu)` or `sqlite3rbu_open(zTarget, zRbu, 0)`, optionally executes `zPreSql` on both the main and RBU database handles, steps the RBU handle up to `nStep` calls or until completion/error, closes the handle with `sqlite3rbu_close()`, reports final status, and returns success only for `SQLITE_OK` or `SQLITE_DONE`.

The RBU API calls are `sqlite3rbu_open()`, `sqlite3rbu_vacuum()`, `sqlite3rbu_db()`, `sqlite3rbu_step()`, `sqlite3rbu_progress()`, `sqlite3rbu_bp_progress()`, and `sqlite3rbu_close()`.

## Control Flow

The program requires at least two trailing positional arguments. It treats `argc-2` and `argc-1` as the target and RBU/state database paths. Options before those arguments configure mode and limits. `-step` controls the maximum number of `sqlite3rbu_step()` calls; when less than or equal to zero, stepping is unbounded until the update finishes or an error occurs. `-statstep` prints memory statistics every configured number of loop iterations. `-vacuum` switches from update mode to RBU vacuum mode. `-presql` captures a SQL string to run after opening the RBU handle and before stepping.

After parsing, the program prints the default VFS, opens the RBU handle, and reports the VFS used by the target connection. If pre-SQL is requested and the handle exists, it runs the SQL first against the main connection (`sqlite3rbu_db(pRbu, 0)`) and then against the RBU/state connection (`sqlite3rbu_db(pRbu, 1)`) only if the first execution succeeds.

The stepping loop calls `sqlite3rbu_step(pRbu)` in the loop condition. Each successful `SQLITE_OK` step increments `i`. If stat reporting is enabled and `i % nStatStep == 0`, the program prints memory usage/highwater via `sqlite3_status64()`. In non-vacuum mode it also prints backfill progress from `sqlite3rbu_bp_progress()`.

When the loop exits, the program reads `sqlite3rbu_progress(pRbu)`, closes the handle, and lets `sqlite3rbu_close()` determine whether the operation is incomplete (`SQLITE_OK`), complete (`SQLITE_DONE`), or failed. It prints a final message, optional final memory stats, frees any close error message, and exits 0 for incomplete-or-complete success and 1 for failures.

## State And Persistence Behavior

Durable state is managed by the RBU library and the databases named on the command line. If `nStep` limits work before completion, `sqlite3rbu_close()` saves resumable state in the RBU database for update mode or the state database for vacuum mode. A later invocation can resume through the same library APIs. The driver itself has no separate state file.

The program may mutate both target and RBU/state databases. Normal update mode applies changes from the RBU database into the target. Vacuum mode uses RBU to vacuum the target using the second database as the state store. `-presql` is especially powerful because it executes arbitrary SQL against both opened connections before stepping.

In-process state includes counters, progress totals, an optional error string from `sqlite3rbu_close()`, and transient VFS-name strings returned by file control.

## Dependencies And Integration Points

The file depends on `sqlite3rbu.h` plus C standard headers `stdio.h`, `stdlib.h`, and `string.h`. It also indirectly uses SQLite APIs exposed by the RBU header, including VFS discovery, file-control, status counters, and memory cleanup.

The integration point is a compiled CLI linked with the RBU extension implementation. It is useful in test scripts and manual update/vacuum workflows where bounded calls demonstrate resumability. The surrounding `ext/rbu` directory contains many Tcl tests for RBU behavior, including crash/resume, vacuum, fault injection, and progress cases; this driver is the simple executable interface to the same library.

## Risks And Edge Cases

Option parsing allows prefixes such as `-s` for `-step` and `-v` for `-vacuum` as long as they satisfy the length guard. This is convenient but can make ambiguous future option additions risky. Numeric options use `atoi()`, so invalid strings silently become zero and negative values mean unbounded stepping.

The code does not explicitly check for a failed `sqlite3rbu_open()` or `sqlite3rbu_vacuum()` before the stepping block. If `pRbu` is NULL and `rc` remains `SQLITE_OK`, the later `sqlite3rbu_step(pRbu)`, `sqlite3rbu_progress(pRbu)`, or `sqlite3rbu_close(pRbu, ...)` behavior depends on the RBU API's NULL handling. The VFS report function itself tolerates a NULL or unusable handle only through `sqlite3rbu_db()` returning NULL.

`zPreSql` errors prevent stepping and also skip `sqlite3rbu_close()`, because close is only called inside the `rc==SQLITE_OK` stepping block. If a handle was opened and pre-SQL fails, this path risks not closing the RBU handle before exit. This matters for resource cleanup and possibly for any open transaction state controlled by the RBU handle.

Progress reporting prints at `i==0` after the first successful step because `i` is incremented after the loop body. That is observable but likely harmless. Format strings use `%lld` with `sqlite3_int64`; SQLite's supported platforms generally make this acceptable, but strictly portable code often casts to `long long`.

## Test Signals

CLI tests should cover update and vacuum modes, unbounded stepping, small positive `-step` followed by resume, `-statstep`, and `-presql` success/failure against both handles. Error tests should include missing arguments, malformed numeric arguments, invalid RBU database, invalid target path, VFS reporting without available VFS name, RBU open failure, and close-time error messages.

RBU integration tests should verify that `SQLITE_OK` means incomplete resumable success, `SQLITE_DONE` means complete success, and all other result codes exit non-zero. Crash/resume and bounded-step tests from the `ext/rbu` suite are the strongest behavioral signals because this program relies almost entirely on the library for persistence and correctness.
