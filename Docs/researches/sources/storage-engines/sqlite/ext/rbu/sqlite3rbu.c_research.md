# sources/storage-engines/sqlite/ext/rbu/sqlite3rbu.c

## Purpose

`sqlite3rbu.c` implements SQLite's Resumable Bulk Update extension. It applies large INSERT/UPDATE/DELETE batches from a separate RBU database to a target database while keeping partial work hidden from ordinary readers, then makes the update visible by renaming an `*-oal` file to `*-wal` and incrementally checkpointing it. The same implementation also supports resumable RBU vacuum, where the target is rebuilt into a temporary database-like image and then checkpointed. The file includes the public API implementation, SQL-generation machinery for target table/index updates, persistent state handling, a Fossil-delta SQL helper, and a custom VFS shim that redirects WAL operations and captures checkpoint I/O.

## Important APIs, Types, and Functions

The opaque public handle is `struct sqlite3rbu`. It owns the target and RBU `sqlite3` handles, path/state strings, current stage, error state, object iterator, RBU VFS name, target file descriptor, checkpoint frame list, progress counters, temp-space accounting, and rename callback. `RbuState` mirrors rows in `rbu_state`; its fields store current stage, target/data table, index, row offset, progress, WAL checksum, database cookie, OAL size, and phase-one estimate. `RbuObjIter` walks all RBU source tables and associated target b-trees, caching target column metadata, PK/index shape, SQL statements, and an LRU list of generated UPDATE statements. `rbu_vfs` and `rbu_file` implement the VFS layer used to intercept WAL/OAL/shm/temp-file behavior.

Public entry points are `sqlite3rbu_open()`, `sqlite3rbu_vacuum()`, `sqlite3rbu_step()`, `sqlite3rbu_savestate()`, `sqlite3rbu_close()`, `sqlite3rbu_db()`, `sqlite3rbu_progress()`, `sqlite3rbu_bp_progress()`, `sqlite3rbu_state()`, `sqlite3rbu_rename_handler()`, `sqlite3rbu_create_vfs()`, `sqlite3rbu_destroy_vfs()`, `sqlite3rbu_temp_size_limit()`, and `sqlite3rbu_temp_size()`. `openRbuHandle()` is the central constructor used by both open modes.

Major internal subsystems include Fossil-delta helpers (`rbuDeltaGetInt()`, `rbuDeltaApply()`, `rbuFossilDeltaFunc()`), object iteration (`rbuObjIterFirst()`, `rbuObjIterNext()`, `rbuObjIterPrepareAll()`), target metadata discovery (`rbuTableType()`, `rbuObjIterCacheTableInfo()`, `rbuObjIterCacheIndexedCols()`), imposter-table creation (`rbuCreateImposterTable()`, `rbuCreateImposterTable2()`), SQL list generation (`rbuObjIterGetCollist()`, `rbuObjIterGetWhere()`, `rbuObjIterGetSetlist()`, `rbuObjIterGetIndexCols()`), statement execution (`rbuStepType()`, `rbuStepOneOp()`, `rbuStep()`), state persistence (`rbuLoadState()`, `rbuSaveState()`, `rbuSetupOal()`), and checkpoint preparation (`rbuSetupCheckpoint()`, `rbuCaptureWalRead()`, `rbuCaptureDbWrite()`, `rbuCheckpointFrame()`).

## Control Flow

`sqlite3rbu_open()` validates arguments and calls `openRbuHandle()`, which creates a private RBU VFS, opens the RBU/state/target databases through it, creates or attaches the `rbu_state` table, registers helper SQL functions, loads saved state, checks the database cookie, and configures the first stage. New updates start in `RBU_STAGE_OAL`; resumed updates may restart in OAL, move, checkpoint, or done state. WAL-mode target databases are rejected for normal updates because RBU needs to build a hidden OAL before exposing WAL content.

During `RBU_STAGE_OAL`, each `sqlite3rbu_step()` advances the `RbuObjIter`. For each source `data_*` table, the iterator visits the target table b-tree, then each auxiliary index b-tree, then a cleanup state. `rbuObjIterPrepareAll()` lazily builds the SQL needed for the current object. Table b-trees are modified through imposter tables unless the target is a virtual table. Index b-trees are updated by creating a WITHOUT ROWID imposter table over the index root page and selecting sorted keys from `data_*` or state temp tables. `rbuStep()` interprets `rbu_control` as insert, delete, replace, index delete, index insert, or update mask and executes one logical operation. When all objects are processed, RBU saves move-stage state, increments the schema cookie, commits both databases, and advances to `RBU_STAGE_MOVE`.

During `RBU_STAGE_MOVE`, `rbuMoveOalFile()` closes and reopens handles, obtains an exclusive lock, renames `*-oal` to `*-wal` through either the default or user-supplied rename callback, then reopens the database and initializes checkpoint capture. In `RBU_STAGE_CKPT`, each `sqlite3rbu_step()` copies WAL frames into the database file. It checkpoints enough adjacent frames to avoid saving state mid-sector when the sector size is larger than the page size, syncs the database at completion, updates WAL-index backfill, sets `RBU_STAGE_DONE`, and returns `SQLITE_DONE`.

`sqlite3rbu_close()` commits any pending OAL transaction, syncs during checkpoint state, saves `rbu_state`, closes statements and database handles, tears down the private VFS, returns or frees the error message, and releases all allocations. `sqlite3rbu_savestate()` is an explicit mid-run checkpoint: it commits OAL work, syncs if checkpointing, writes `rbu_state`, and reopens transactions so further `step()` calls may continue.

## State and Persistence Behavior

The durable state table is `%s.rbu_state(k INTEGER PRIMARY KEY, v)`. Keys encode stage, target table, index, row offset, progress, checkpoint checksum, database change-counter cookie, OAL size, phase-one step estimate, and current RBU data table. This lets a later process resume within a table/index by skipping rows with `LIMIT -1 OFFSET n` or, for RBU vacuum, by deriving key-range starts when possible.

The target database is not modified directly in rollback journal mode. OAL-stage modifications are written through SQLite WAL machinery to an `*-oal` file whose existence is hidden from ordinary clients. The VFS records the original page-1 change-counter cookie and rejects resume if it no longer matches, which detects an external writer between suspend and resume. Once OAL is renamed to WAL, the update becomes visible to ordinary readers before checkpointing finishes.

Checkpoint persistence uses the saved row count (`RBU_STATE_ROW`) as the number of already checkpointed frame entries plus a saved WAL-index checksum. On resume, `rbuSetupCheckpoint()` captures the would-be checkpoint frame list again and compares the WAL-index checksum to the saved value. If another client has appended frames, RBU treats the operation as done rather than continuing a stale incremental checkpoint.

Temp-file state is tracked per VFS file via `rbuUpdateTempSize()` and aggregated in `sqlite3rbu.szTemp`; the public limit API can force `SQLITE_FULL` if temporary files grow beyond the configured threshold. RBU vacuum may create a state database and an internal `-vactmp` target and copies target schema plus selected PRAGMAs into the rebuilt database.

## Dependencies and Integration Points

This file depends heavily on SQLite's public C API and a small number of SQLite-specific extension hooks: `SQLITE_TESTCTRL_IMPOSTER` for writing directly to table/index b-trees, `SQLITE_FCNTL_RBU` and `SQLITE_FCNTL_RBUCNT` for VFS file-control plumbing, `SQLITE_FCNTL_ZIPVFS` and a copied ZipVFS file-pointer control for ZipVFS compatibility checks, WAL shared-memory locking conventions, URI options, and schema/PRAGMA introspection. It registers SQL functions `rbu_target_name`, `rbu_tmp_insert`, `rbu_fossil_delta`, and optionally `rbu_index_cnt`.

Input integration is through RBU database tables or views named `data_<target>` or `dataNNN_<target>`, optional `rbu_count`, and `rbu_control` values. Target integration covers ordinary rowid tables, INTEGER PRIMARY KEY tables, external primary-key tables, WITHOUT ROWID tables, and virtual tables. For virtual tables and no-PK tables, `rbu_rowid` is required. For partial indexes and expression indexes, the code reads `sqlite_schema.sql` and `PRAGMA index_xinfo` to generate the right sorted data streams and imposter table shape.

The VFS layer integrates by wrapping a parent VFS and proxying all normal operations except when RBU stage-specific behavior is required. It can be automatically private per handle or explicitly created for ZipVFS stacks. Rename integration is injectable via `sqlite3rbu_rename_handler()`, which is important for tests and for non-POSIX storage layers.

## Risks and Edge Cases

The file itself documents risks around non-portable rename behavior, lack of atomicity between OAL commits and RBU-state commits, and unclear recovery when an external writer changes the target mid-update. The implementation mitigates some of this with page-1 cookie checks and checkpoint checksums, but the OAL/state split still leaves crash windows where replay may see constraint errors or already-applied work.

The VFS shim is highly sensitive to SQLite WAL internals: WAL lock numbers, page-header offsets, WAL frame layout, shared-memory checksum offsets, and file-name pointer identity are assumed stable. Bugs in this layer could expose partial updates, accidentally checkpoint OAL content, leak SHM locks, or mis-handle stacked VFS configurations. `rbuVfsAccess()` deliberately returns `SQLITE_CANTOPEN` if an existing WAL is detected during OAL stage, so damaged page-1 state or unusual VFS behavior can surface as open failures.

SQL generation is complex for expression indexes, partial indexes, external primary keys, WITHOUT ROWID tables, virtual tables, update masks, and `rbu_delta`/`rbu_fossil_delta`. Invalid `rbu_control` values produce `SQLITE_ERROR`; NULL explicit INTEGER PRIMARY KEY insertions produce `SQLITE_MISMATCH`. If a user-defined `rbu_delta()` is not registered when a mask uses `d`, execution fails through SQLite statement errors.

RBU vacuum has additional risk because it synthesizes page-1 reads and creates a target schema under `PRAGMA writable_schema=1`. It refuses WAL-mode vacuum cases and reserves state names ending in `-vactmp`, but any mismatch between source schema, state database, and VFS stack can leave an error state and reset vacuum state tables.

## Test Signals

The companion `test_rbu.c` exposes the public API to Tcl tests. The surrounding RBU test suite in `ext/rbu` exercises ordinary updates, vacuum, resumption, busy handling, crashes, faults, rename handling, progress, temp-size limits, FTS/virtual tables, collations, partial indexes, split state databases, and VFS behavior. Implementation-level assertions also signal invariants around iterator state, WAL locks, stage transitions, and imposter-table assumptions.
