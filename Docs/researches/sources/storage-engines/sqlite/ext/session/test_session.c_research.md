# sources/storage-engines/sqlite/ext/session/test_session.c

## Purpose

This file is a Tcl test extension for the SQLite session module, compiled only when `SQLITE_TEST`, `SQLITE_ENABLE_SESSION`, and `SQLITE_ENABLE_PREUPDATE_HOOK` are all defined. It wraps session, changeset, changegroup, apply, rebase, and streaming APIs as Tcl commands so the SQLite test suite can generate, inspect, mutate, apply, validate, and combine changesets from Tcl scripts.

## Important APIs, Types, and Functions

`TestSession` stores a `sqlite3_session*`, Tcl interpreter, and optional table-filter script. `TestStreamInput` models chunked input for streaming APIs using a byte buffer, current offset, and maximum chunk size. `TestSessionsBlob` accumulates streaming output into a reallocating buffer. `TestConflictHandler` keeps conflict and filter Tcl scripts for apply callbacks. `TestChangegroup` and `TestChangeIter` wrap changegroup and iterator handles as Tcl command objects.

Key command implementations are `test_sqlite3session()`, `test_session_cmd()`, `testSqlite3changesetApply()`, `test_sqlite3changeset_invert()`, `test_sqlite3changeset_concat()`, `test_sqlite3session_foreach()`, `test_sqlite3rebaser_create()`, `test_rebaser_cmd()`, `test_changeset()`, `test_sqlite3session_config()`, `test_sqlite3changegroup()`, `test_changegroup_cmd()`, `test_sqlite3changeset_start()`, and `test_iter_cmd()`. `TestSession_Init()` registers the Tcl command surface.

The helper `sql_exec_changeset()` is copied from the session documentation and verifies that the documented example remains executable. `sqlite3_test_changeset()` performs structural sanity checks on changesets and patchsets, especially update old/new value presence rules.

## Control Flow

The session command flow starts with `sqlite3session CMD DB-HANDLE DB-NAME`, which resolves a Tcl SQLite database command into `sqlite3*`, creates a session, enables size accounting by default after verifying it is initially disabled, and registers a new Tcl object command. That object supports subcommands for `attach`, `changeset`, `patchset`, `delete`, `enable`, `indirect`, `isempty`, `table_filter`, `diff`, `memory_used`, `changeset_size`, and `object_config`. Changeset and patchset output can use either normal APIs or streaming APIs depending on the global Tcl variable `sqlite3session_streams`.

Apply flow is centralized in `testSqlite3changesetApply()`, parameterized by version 1, 2, or 3. It parses flags for v2/v3, copies the Tcl byte array into exact malloc-sized memory for ASAN-sensitive tests, wires optional filter scripts, and invokes normal or streaming apply APIs. The conflict callback builds a Tcl list containing operation type, table, conflict type, old/new rows, and conflicting row when available. It also deliberately calls accessor APIs in invalid modes or ranges to assert `SQLITE_MISUSE` and `SQLITE_RANGE`.

Iterator and foreach flow copies the changeset, starts an iterator with optional inversion and optional streaming, converts each change to a Tcl structure via `testIterData()`, and either drives a Tcl script or exposes a Tcl iterator command with `next`, `data`, and `finalize` subcommands. Rebaser flow wraps create/configure/rebase/delete and supports streaming rebase. Changegroup flow wraps schema, add, output, add_change, patchset config, and the one-at-a-time change construction APIs.

## State and Persistence

Most persistent state is attached to Tcl commands through `objClientData` and cleaned by destructors. `test_session_del()` decrements filter script references and deletes the session. `test_rebaser_del()`, `test_changegroup_del()`, and `test_iter_del()` release their SQLite handles. Streaming state is transient per command call, except a streaming iterator stores its own copy of the input bytes after the `TestChangeIter` struct so callbacks remain valid for the iterator lifetime. Several APIs intentionally allocate with plain `malloc()` instead of Tcl or SQLite allocators to make ASAN and valgrind catch small overreads.

## Dependencies and Integration Points

The file depends on `sqlite3session.h`, `tclsqlite.h`, Tcl object APIs, SQLite test helpers such as `sqlite3ErrName()`, and the session extension. It is tightly integrated with SQLite's Tcl test runner: database handles are looked up from Tcl command names, errors are surfaced as Tcl result strings, and callback scripts are evaluated in the global interpreter context. It also integrates with SQLite fault injection by allocating inside `testStreamInput()` so streaming callbacks can fail with `SQLITE_NOMEM`.

## Risks and Edge Cases

The test harness intentionally exercises undefined or edge behaviors, so it is not application code. Tcl script callbacks can background errors, conflict callbacks can return numeric values outside symbolic strings, and many paths assume assertions are active in debug tests. Streaming behavior depends on `sqlite3session_streams`; setting it changes the API path without changing Tcl commands. Exact-sized byte copies are important for memory-safety tests. `test_iter_del()` finalizes the iterator, while the `finalize` subcommand also finalizes and nulls it before deleting the Tcl command; this relies on Tcl deletion ordering not to double-finalize a live pointer.

## Test Signals

This file is itself the test signal for `sqlite3session.h`. It validates documented examples, normal and streaming changeset creation, inversion, concatenation, apply v1/v2/v3, rebase output, iterator inspection, conflict handler accessor legality, changegroup merging and construction, and session global configuration. The `assert_changeset_is_ok()` macro adds structural validation in debug builds after many generated outputs.
