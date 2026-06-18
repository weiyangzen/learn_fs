# sources/storage-engines/sqlite/ext/session/sqlite3session.h

## Purpose

This header is the public C API contract for SQLite's session extension when `SQLITE_ENABLE_SESSION` is enabled. It declares opaque session, changeset iterator, changegroup, and rebaser handles and documents the lifecycle and behavior of capturing database mutations, producing changesets or patchsets, iterating and applying them, merging them, rebasing local work after remote conflict resolution, and using streaming variants for large inputs.

## Important APIs, Types, and Constants

The main opaque types are `sqlite3_session`, `sqlite3_changeset_iter`, `sqlite3_changegroup`, and `sqlite3_rebaser`. Session lifecycle and capture APIs include `sqlite3session_create()`, `sqlite3session_delete()`, `sqlite3session_object_config()`, `sqlite3session_enable()`, `sqlite3session_indirect()`, `sqlite3session_attach()`, `sqlite3session_table_filter()`, `sqlite3session_changeset()`, `sqlite3session_patchset()`, `sqlite3session_diff()`, `sqlite3session_isempty()`, and `sqlite3session_memory_used()`.

Iterator APIs include `sqlite3changeset_start()`, `sqlite3changeset_start_v2()`, `sqlite3changeset_next()`, `sqlite3changeset_op()`, `sqlite3changeset_pk()`, `sqlite3changeset_old()`, `sqlite3changeset_new()`, `sqlite3changeset_conflict()`, `sqlite3changeset_fk_conflicts()`, and `sqlite3changeset_finalize()`. Transform and merge APIs include `sqlite3changeset_invert()`, `sqlite3changeset_concat()`, `sqlite3changegroup_new()`, `sqlite3changegroup_schema()`, `sqlite3changegroup_add()`, `sqlite3changegroup_add_change()`, `sqlite3changegroup_output()`, and `sqlite3changegroup_delete()`.

Apply APIs are `sqlite3changeset_apply()`, `sqlite3changeset_apply_v2()`, and `sqlite3changeset_apply_v3()`. The v2 and v3 forms add rebase output and flags. Key flags are `SQLITE_CHANGESETSTART_INVERT`, `SQLITE_CHANGESETAPPLY_NOSAVEPOINT`, `SQLITE_CHANGESETAPPLY_INVERT`, `SQLITE_CHANGESETAPPLY_IGNORENOOP`, `SQLITE_CHANGESETAPPLY_FKNOACTION`, and `SQLITE_CHANGESETAPPLY_NOUPDATELOOP`. Conflict reasons are `SQLITE_CHANGESET_DATA`, `SQLITE_CHANGESET_NOTFOUND`, `SQLITE_CHANGESET_CONFLICT`, `SQLITE_CHANGESET_CONSTRAINT`, and `SQLITE_CHANGESET_FOREIGN_KEY`; conflict handler return values are `SQLITE_CHANGESET_OMIT`, `SQLITE_CHANGESET_REPLACE`, and `SQLITE_CHANGESET_ABORT`.

Rebase APIs are `sqlite3rebaser_create()`, `sqlite3rebaser_configure()`, `sqlite3rebaser_rebase()`, and `sqlite3rebaser_delete()`. Streaming variants replace contiguous changeset buffers with `xInput` and `xOutput` callbacks for apply, concat, invert, start, session output, changegroup I/O, and rebase. Global/session configuration is exposed through `sqlite3session_config(SQLITE_SESSION_CONFIG_STRMSIZE, ...)`, and changegroup output mode can be set with `sqlite3changegroup_config(SQLITE_CHANGEGROUP_CONFIG_PATCHSET, ...)`.

The tail adds one-at-a-time change construction APIs for changegroups: `sqlite3changegroup_change_begin()`, typed value functions for int64, null, double, text, and blob, and `sqlite3changegroup_change_finish()`.

## Control Flow and Behavior

A normal capture flow is: create a session for a database name, optionally configure rowid or size tracking before attaching tables, attach one table or all tables, perform writes while the session is enabled, and then emit a changeset or patchset. The header explains that sessions store primary-key information and original row values on first touch, then query current database state at output time to decide whether each tracked row is an INSERT, UPDATE, DELETE, or no-op. Primary key changes are represented as delete plus insert, and rows with NULL primary-key columns are ignored. Tables are grouped in attach order.

Apply flow validates compatible target tables, optionally filters by table or per-change iterator depending on API version, applies each operation inside a savepoint by default, and invokes conflict handlers for data mismatches, missing rows, duplicate primary keys, constraint failures, and final foreign-key violations. Conflict handlers may omit, replace where allowed, or abort. The v2/v3 APIs may also produce a rebase blob when conflicts occurred, which later configures a rebaser for local changesets.

Changegroups combine multiple changesets or patchsets by primary key. Rules are explicitly defined for every pair of existing and incoming operation types, such as insert plus delete canceling out, update plus update merging column changes, and delete plus insert becoming update or no-op. The schema API allows combining compatible but different-column-count changesets against a configured database schema.

## State and Persistence

The header itself persists no state, but it defines several stateful object lifecycles. A session is attached to a `sqlite3*` and uses the preupdate hook, so it must be deleted before the database handle closes and cannot coexist with another preupdate hook on the same connection. Session state includes enabled/disabled capture, indirect-change marking, attached tables, optional table filter, object configuration, and accumulated row records. Changeset and patchset buffers are heap allocations owned by callers and freed with `sqlite3_free()`. Iterators borrow their input buffers until finalized. Changegroups and rebasers own accumulated in-memory state until deleted. Streaming callbacks move persistence responsibility to caller-managed input/output contexts.

## Dependencies and Integration Points

The header includes `sqlite3.h` and is guarded by `SQLITE_ENABLE_SESSION`. It integrates deeply with SQLite preupdate hooks, SQLite value objects, database schema inspection, conflict callbacks, SQLite error codes, savepoints, `sqlite3_log()`, and foreign-key enforcement. It also defines compatibility expectations for downstream bindings, Tcl tests, WASM builds with session enabled, and applications that sync databases through changesets.

## Risks and Edge Cases

Major risks are misuse of object lifetimes, assuming sessions can coexist with arbitrary preupdate hooks, failing to free output buffers, using iterators after their input buffer has gone away, returning illegal conflict actions, or applying patchsets where old values are required for conflict detection. `sqlite3changeset_invert()` explicitly warns that invalid input has undefined results. Global `sqlite3session_config()` is not threadsafe and must run before session objects exist. `SQLITE_SESSION_OBJCONFIG_SIZE` and `SQLITE_SESSION_OBJCONFIG_ROWID` must be modified before table attachment. Streaming callbacks can leave iterators in persistent error states if they fail.

## Test Signals

The related `test_session.c` file exercises nearly all declared APIs through Tcl commands, including streaming and non-streaming paths, conflict handler behavior, range and misuse errors for iterator accessors, rebase flow, changegroup APIs, and constructed changes. The WASM makefile enables `SQLITE_ENABLE_SESSION` in full-featured builds, so this header is also part of the JS/WASM API build surface.
