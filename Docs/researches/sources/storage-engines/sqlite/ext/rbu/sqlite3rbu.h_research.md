# sources/storage-engines/sqlite/ext/rbu/sqlite3rbu.h

## Purpose

`sqlite3rbu.h` declares the public C interface and user-facing contract for the RBU extension. Its long header comments define what an RBU update is, how an RBU database must be laid out, how resumable updates and RBU vacuum work, which SQL features are intentionally unsupported, what locking behavior callers should expect, and how applications should drive the API.

## Important APIs, Types, and Constants

The only public type is opaque `sqlite3rbu`. Applications allocate it with `sqlite3rbu_open()` for update mode or `sqlite3rbu_vacuum()` for vacuum mode, drive work with `sqlite3rbu_step()`, optionally force state persistence with `sqlite3rbu_savestate()`, and release it with `sqlite3rbu_close()`.

`sqlite3rbu_db()` exposes the internal target or RBU database handle so callers can register virtual table modules or SQL functions such as `rbu_delta()`. `sqlite3rbu_progress()` returns a monotonically increasing count of key-value operations. `sqlite3rbu_bp_progress()` reports two permyriad progress values: phase one for building OAL/WAL content and phase two for checkpointing. `sqlite3rbu_state()` returns `SQLITE_RBU_STATE_OAL`, `SQLITE_RBU_STATE_MOVE`, `SQLITE_RBU_STATE_CHECKPOINT`, `SQLITE_RBU_STATE_DONE`, or `SQLITE_RBU_STATE_ERROR`.

`sqlite3rbu_rename_handler()` allows callers to replace the default filesystem rename used when moving `*-oal` to `*-wal`. `sqlite3rbu_create_vfs()` and `sqlite3rbu_destroy_vfs()` expose the RBU VFS shim for explicit VFS stack construction, especially with ZipVFS. `sqlite3rbu_temp_size_limit()` and `sqlite3rbu_temp_size()` configure and report aggregate temporary-file usage.

## Control Flow

The intended update loop is: open a handle, register required modules/functions on handles returned by `sqlite3rbu_db()`, call `sqlite3rbu_step()` until it returns something other than `SQLITE_OK`, then call `sqlite3rbu_close()` and inspect both return code and optional error message. A partial run can be stopped with `sqlite3rbu_close()` or `sqlite3rbu_savestate()`; later callers use the same target/RBU/state paths to resume.

The header divides execution into visible stages. In OAL state, RBU is building a hidden `*-oal` file and ordinary clients keep reading the old database. In MOVE state, the next step renames the OAL to WAL and makes the update visible. In CHECKPOINT state, RBU copies WAL pages back into the database incrementally. DONE and ERROR are terminal states for the current handle.

For RBU vacuum, callers open with `sqlite3rbu_vacuum(target, state)`, repeatedly step, and close. The state database may be explicit or default to `<database>-vacuum`. State database names ending in `-vactmp` are reserved for internal use.

## State and Persistence Behavior

If `zState` is NULL for update mode, state is stored inside the RBU database. If non-NULL, it names a separate state database that must be reused for resumption. For vacuum mode, the state database is not automatically deleted on success; if close returns an error, the implementation clears the state tables so the next vacuum begins from scratch.

The header emphasizes that a suspended update may be resumed after process exit or crash from the most recently saved state. It also documents that if an external client writes to the target database between suspension and resumption, resuming returns `SQLITE_BUSY`.

Temp-space state is exposed as a per-handle aggregate. A nonzero limit causes `SQLITE_FULL` if RBU's temporary files exceed it. Progress state depends on optional `rbu_count`; if present and correctly populated, phase-one progress can be estimated, otherwise phase one reports `-1`.

## Dependencies and Integration Points

The header includes `sqlite3.h` for SQLite types and result codes and supports C++ callers with `extern "C"`. It requires callers to create RBU source tables named `data_<target>` or `dataNNN_<target>`, each with target columns plus `rbu_control` and sometimes `rbu_rowid`. `rbu_control` integer values represent insert/delete/replace, while text masks with `x`, `.`, `d`, and `f` describe updates and delta application.

Target virtual tables require callers to register modules on the target handle. RBU source virtual tables or views require modules on the RBU handle. Use of `d` update masks requires a caller-provided `rbu_delta()` function. Fossil-delta masks use the built-in implementation from the C file. ZipVFS integration requires an explicit VFS stack with the RBU VFS below ZipVFS and above lower storage layers.

## Risks and Contract Limits

RBU transactions are limited to INSERT, UPDATE, and DELETE semantics. Defaults, triggers, foreign-key checks, CHECK constraints, and most conflict handling are not supported. UPDATE and DELETE must identify rows by non-NULL primary-key values or rowid, and UPDATE may not modify primary-key columns. RBU does not run a general SQL transaction engine over arbitrary statements; callers must encode data exactly as documented.

The API returns stable SQLite result codes, but database handles from `sqlite3rbu_db()` are only valid until the next RBU API call other than another `sqlite3rbu_db()`. Destroying an RBU VFS while database handles still use it is undefined. Once `sqlite3rbu_step()` returns a non-`SQLITE_OK` value, later step calls on the same handle return the same value without doing work.

## Test Signals

The header's documented APIs are directly wrapped by `test_rbu.c`, making Tcl tests able to drive update/vacuum loops, inspect state/progress, register delta functions, inject rename callbacks, and manipulate temp-size limits. The extensive examples and constraints in this header are the behavioral oracle for the `ext/rbu/*.test` suite.
