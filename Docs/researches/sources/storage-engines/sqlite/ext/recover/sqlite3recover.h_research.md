# sources/storage-engines/sqlite/ext/recover/sqlite3recover.h

## Purpose

`sqlite3recover.h` is the public C interface for SQLite's recover extension. It documents the lifecycle for recovering data from a corrupt database into either a replacement database file or a stream of SQL statements and defines the configuration options understood by the implementation.

## Important APIs, Types, and Functions

The header exposes an opaque `sqlite3_recover` type and eight API functions: `sqlite3_recover_init()`, `sqlite3_recover_init_sql()`, `sqlite3_recover_config()`, `sqlite3_recover_step()`, `sqlite3_recover_run()`, `sqlite3_recover_errmsg()`, `sqlite3_recover_errcode()`, and `sqlite3_recover_finish()`.

The configuration constants are `SQLITE_RECOVER_LOST_AND_FOUND`, `SQLITE_RECOVER_FREELIST_CORRUPT`, `SQLITE_RECOVER_ROWIDS`, and `SQLITE_RECOVER_SLOWINDEXES`. Their argument conventions are part of the public contract: lost-and-found takes a nullable string pointer, while the other three take a pointer to an `int` boolean.

## Control Flow

The intended caller flow is: allocate with one of the init functions, configure before any step/run call, repeatedly call `sqlite3_recover_step()` until it stops returning `SQLITE_OK`, inspect error state if needed, then always call `sqlite3_recover_finish()`. `sqlite3_recover_run()` is documented as the convenience loop around `sqlite3_recover_step()` followed by `sqlite3_recover_errcode()`.

The header also defines completion semantics: `SQLITE_DONE` means recovery finished successfully; other non-`SQLITE_OK` returns are errors; inability to recover all corrupt data is not itself an API error. After `sqlite3_recover_step()` returns anything other than `SQLITE_OK`, further step calls are no-ops returning the same non-OK state.

## State and Persistence Behavior

`sqlite3_recover` is opaque, so callers cannot mutate internal state directly. The input state is an already opened SQLite handle plus an attached database name such as `main`, `temp`, or another attached schema. In output-database mode, `zUri` identifies a database that may be overwritten. In SQL-callback mode, the callback receives statements that should reconstruct the same output if executed in order.

Options modify persistence semantics. Lost-and-found naming controls whether orphan records are materialized into a table. Freelist-corrupt mode decides whether pages that appear on the freelist are treated as recoverable candidates. Rowid mode controls preservation of non-IPK rowids versus assignment of new rowids. Slow-index mode chooses whether non-UNIQUE indexes are built before row insertion or delayed until the end.

## Dependencies and Integration Points

The only included dependency is `sqlite3.h`. The API is C++ compatible through `extern "C"`. It is implemented by `sqlite3recover.c` and test-exposed through `test_recover.c`. Users must supply a live SQLite connection with the source database attached, and they must respect the pre-run-only constraint on `sqlite3_recover_config()`.

## Risks and Edge Cases

The `void *pArg` configuration API is type-sensitive, and misuse is only partly detectable. The callback API aborts recovery if the callback returns anything other than `SQLITE_OK`; applications must avoid returning application-specific error codes accidentally unless they intend to stop recovery.

The header states that abandoning recovery with `finish()` before completion is not an API error, but the output database or partial SQL stream is undefined. Callers should treat partial outputs as disposable unless they layer their own transaction handling around SQL callback replay.

## Test Signals

The Tcl test wrapper in `test_recover.c` maps the documented lifecycle into commands. The `ext/recover` tests exercise both init modes, all documented options, error reporting, finalize semantics, and incremental stepping. Header contract regressions would show up as compile errors, Tcl command argument failures, mismatched SQLite result codes, or recovery tests that can no longer configure options before running.
