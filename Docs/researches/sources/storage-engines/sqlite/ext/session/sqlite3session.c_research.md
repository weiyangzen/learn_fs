# sources/storage-engines/sqlite/ext/session/sqlite3session.c

## Purpose

`sqlite3session.c` implements SQLite's session extension when both `SQLITE_ENABLE_SESSION` and `SQLITE_ENABLE_PREUPDATE_HOOK` are enabled. It records row-level changes on selected tables, serializes them into SQLite changeset or patchset blobs, iterates and inverts those blobs, applies them to another database with conflict callbacks, concatenates change streams through changegroups, and rebases local changes against conflict-resolution records.

The file is self-contained implementation glue around SQLite internals. It uses the public session API declared in `sqlite3session.h`, but depends heavily on SQLite core facilities from `sqliteInt.h`, `vdbeInt.h`, preupdate hooks, VDBE `sqlite3_value` helpers, schema PRAGMAs, mutexes, savepoints, and prepared SQL statements.

## Important Types

- `sqlite3_session`: session handle attached to one `sqlite3` connection and one schema name. It stores enable/indirect flags, auto-attach/table-filter state, size-accounting flags, current error state, memory accounting, linked-list membership on the database handle, tracked tables, and a `SessionHook` abstraction for reading old/new row values.
- `SessionTable`: per-tracked-table metadata and change state. It owns the table name, visible-column count, total-column count, column names, default expressions, preupdate column indexes, primary-key flags, rowid-as-implicit-PK flag, `sqlite_stat1` special-case flag, a hash table of `SessionChange` entries, and an optional defaults statement used by changegroup/schema-extension paths.
- `SessionChange`: one accumulated row change in a table hash bucket. It records operation (`INSERT`, `UPDATE`, `DELETE`), indirect flag, serialized old/PK record bytes, record field count for schema growth, maximum generated-size estimate, and collision-chain pointer.
- `SessionBuffer`: growable byte buffer used for binary changesets, SQL construction, streaming buffers, rebase buffers, and changegroup intermediate records.
- `SessionInput`: abstraction over in-memory input and streaming input. It tracks current/next offsets, buffered bytes, stream callback, EOF, and whether old bytes may be discarded.
- `sqlite3_changeset_iter`: public iterator handle. It combines a `SessionInput`, current table header storage, current operation metadata, patchset/invert/skip-empty flags, current old/new `sqlite3_value` arrays, and optional conflict-row statement.
- `SessionApplyCtx`: per-apply table context. It owns prepared `SELECT`/`INSERT`/`DELETE` statements, cached UPDATE statements, table schema metadata, deferred constraint and rebase buffers, apply flags, and error text.
- `sqlite3_changegroup` and `sqlite3_rebaser`: accumulation structures for merging changesets/patchsets and for applying rebase metadata. `sqlite3_rebaser` embeds a changegroup-style hash table.
- `ChangeData`: state for the incremental `sqlite3changegroup_change_begin/change_xxx/change_finish` APIs.

## Binary Formats

The implementation defines its own architecture-independent record and changeset formats:

- Record fields begin with one type byte: undefined `0x00`, integer, float, text, blob, or SQL NULL. Integers and floats are stored as 8-byte big-endian payloads. Text/blob fields store a varint byte count followed by raw bytes.
- A changeset groups changes by table. A table header starts with `'T'`, then varint column count, one PK byte per column, and a nul-terminated UTF-8 table name. Each change stores op byte, indirect byte, then old/new records depending on op.
- A patchset uses header `'P'` and stores only the data needed to apply without full conflict verification: INSERT full record, DELETE primary-key fields, UPDATE primary-key plus changed fields.
- A rebase blob uses changeset-like table headers followed by INSERT/DELETE entries and a flag indicating whether the original apply conflict was resolved with REPLACE or OMIT.

Key low-level helpers are `sessionVarintPut/Get/GetSafe`, `sessionGetI64`, `sessionPutI64`, `sessionPutDouble`, `sessionSerializeValue`, `sessionSerialLen`, `sessionReadRecord`, `sessionSkipRecord`, `sessionChangesetBufferTblhdr`, and `sessionChangesetBufferRecord`.

## Public API Surface Implemented

Session capture and generation:

- `sqlite3session_create`, `sqlite3session_delete`
- `sqlite3session_attach`, `sqlite3session_table_filter`
- `sqlite3session_enable`, `sqlite3session_indirect`, `sqlite3session_isempty`
- `sqlite3session_diff`
- `sqlite3session_changeset`, `sqlite3session_changeset_strm`
- `sqlite3session_patchset`, `sqlite3session_patchset_strm`
- `sqlite3session_memory_used`, `sqlite3session_object_config`, `sqlite3session_changeset_size`
- `sqlite3session_config`

Changeset iteration and transformation:

- `sqlite3changeset_start`, `sqlite3changeset_start_v2`, and streaming variants
- `sqlite3changeset_next`, `sqlite3changeset_finalize`
- `sqlite3changeset_op`, `sqlite3changeset_pk`, `sqlite3changeset_old`, `sqlite3changeset_new`
- `sqlite3changeset_conflict`, `sqlite3changeset_fk_conflicts`
- `sqlite3changeset_invert`, `sqlite3changeset_invert_strm`
- `sqlite3changeset_concat`, `sqlite3changeset_concat_strm`

Apply APIs:

- `sqlite3changeset_apply`
- `sqlite3changeset_apply_v2`, `sqlite3changeset_apply_v3`
- `sqlite3changeset_apply_strm`, `sqlite3changeset_apply_v2_strm`, `sqlite3changeset_apply_v3_strm`

Changegroup and rebase APIs:

- `sqlite3changegroup_new`, `sqlite3changegroup_delete`
- `sqlite3changegroup_config`, `sqlite3changegroup_schema`
- `sqlite3changegroup_add`, `sqlite3changegroup_add_change`, and streaming add/output variants
- `sqlite3changegroup_output`
- Incremental constructors: `sqlite3changegroup_change_begin`, `_change_int64`, `_change_null`, `_change_double`, `_change_text`, `_change_blob`, `_change_finish`
- `sqlite3rebaser_create`, `sqlite3rebaser_configure`, `sqlite3rebaser_rebase`, `sqlite3rebaser_rebase_strm`, `sqlite3rebaser_delete`

## Control Flow

Session creation installs one SQLite preupdate hook per database handle. `sqlite3session_create()` allocates a session, initializes preupdate hook adapters, links it into the per-connection session list, and registers `xPreUpdate()` as the hook callback. `sqlite3session_delete()` unlinks the handle, restores the hook to the remaining session list head if needed, frees tracked tables and the `sqlite_stat1` zero-blob value.

Change capture flows through `xPreUpdate()`. For each enabled session on the same schema, it locates the target `SessionTable` by explicit attach or auto-attach filter. `sessionPreupdateOneChange()` initializes table metadata using `PRAGMA table_xinfo`, checks schema-column counts, grows the row-change hash table, optionally wraps hooks for `sqlite_stat1`, hashes primary-key values, skips NULL primary keys, finds an existing row change, and records initial row values or PK values. UPDATE events are processed as a DELETE-side old row plus INSERT-side new row so rowid or PK changes can collapse correctly into later generated output.

Changeset generation is deferred until `sqlite3session_changeset()` or `sqlite3session_patchset()`. `sessionGenerateChangeset()` opens a `SAVEPOINT changeset`, revalidates table schemas, extends old records after schema growth using default values, writes table headers, selects current rows by recorded PK, then emits INSERT, UPDATE, or DELETE records. It omits no-op updates and may stream chunks through `xOutput`.

`sqlite3session_diff()` temporarily replaces the session hooks with `SessionDiffCtx` hooks backed by SELECT result columns. It compares an attached source schema against the session schema using generated SQL: rows present only in target become INSERT changes, rows only in source become DELETE changes, and PK-matching rows with non-PK differences become UPDATE changes.

Changeset iteration starts with `sessionChangesetStart()`. `sessionChangesetNextOne()` buffers enough data, reads table headers, validates op bytes, decodes records into old/new `sqlite3_value` arrays or returns raw record pointers for internal consumers, handles inversion, and normalizes patchset UPDATE PK fields into the old array. `sessionChangesetNext()` optionally skips empty UPDATE changes for apply.

Apply flows through `sessionChangesetApplyV23()` into `sessionChangesetApply()`. The apply engine opens a savepoint unless disabled, defers foreign keys, initializes per-table schema and prepared statements, filters tables or individual changes, and calls `sessionApplyOneWithRetry()`. Each operation binds old/new values into generated SQL and handles DATA, NOTFOUND, CONFLICT, CONSTRAINT, and FOREIGN_KEY conflict modes through the user callback. REPLACE may retry UPDATE/DELETE against matching PK rows or delete conflicting rows before INSERT. Constraint failures can be deferred into a retry buffer and revisited after later changes, including an UPDATE delete/reinsert loop for ordering-sensitive constraints.

Changegroup concatenation reads changesets into per-table hash tables. `sessionOneChangeToHash()` hashes by PK, removes any existing change for the same row, and delegates operation-pair folding to `sessionChangeMerge()`. The merge matrix collapses sequences such as INSERT+UPDATE to INSERT, INSERT+DELETE to no change, DELETE+INSERT to UPDATE, UPDATE+DELETE to DELETE, and UPDATE+UPDATE to a merged UPDATE. `sessionChangegroupOutput()` serializes the accumulated tables back to a changeset or patchset.

Rebase uses the same hash machinery with special record markers. Apply-v2/v3 may collect rebase records in `sessionRebaseAdd()`. `sqlite3rebaser_configure()` hashes those records, and `sessionRebase()` walks a local changeset, rewriting INSERT/UPDATE/DELETE entries against matching remote conflict records. It can convert local INSERT to UPDATE, UPDATE to INSERT or partial UPDATE, DELETE to merged DELETE, or omit resolved pieces depending on indirect/replaced markers.

## State and Persistence Behavior

This file does not persist session state to database tables. Runtime state is heap-resident in session/changegroup/rebaser handles and serialized only when the caller asks for changeset, patchset, rebase, or changegroup output buffers.

Captured session changes store the original row image needed to later compute deltas against the live database. Table-level hash tables grow dynamically and are keyed by serialized primary-key values. The session object tracks allocation sizes for `sqlite3session_memory_used()` and, if configured before attaching tables, estimates maximum changeset size for `sqlite3session_changeset_size()`.

Database writes occur only in apply paths and are wrapped in savepoints by default. Apply temporarily sets `PRAGMA defer_foreign_keys = 1`; optional flags can bypass the savepoint, invert application, ignore no-op conflicts, disable the update-loop constraint retry, or alter FK no-action behavior through internal database flags. Generated changesets are produced under a read savepoint named `changeset` to stabilize SELECTs while collecting current row state.

Schema drift is partially supported. If a table has gained non-PK columns since changes were recorded, old records can be extended using column default expressions. Primary-key layout changes, fewer columns than before, rowid-mode changes, or incompatible apply schemas are treated as schema errors or logged mismatches.

## Dependencies and Integration Points

- Requires SQLite compiled with session and preupdate-hook support.
- Uses SQLite core internal APIs and structs: `sqlite3_preupdate_hook`, `sqlite3_preupdate_old/new/count/depth`, `sqlite3_preupdate_blobwrite`, `sqlite3ValueNew`, `sqlite3ValueSetStr`, `sqlite3ValueFree`, `sqlite3VdbeMemSetInt64`, `sqlite3VdbeMemSetDouble`, `sqlite3_msize`, database mutexes, schema cookies, and internal db flags.
- Discovers schemas using `PRAGMA table_xinfo`, `PRAGMA table_list`, `sqlite3_table_column_metadata`, and direct reads from `sqlite_schema`.
- Generates SQL with identifier quoting for SELECT/INSERT/UPDATE/DELETE operations against the `main` schema during apply and against configured schemas during capture/diff.
- Treats `sqlite_stat1` specially because its logical key is `(tbl, idx)` even though the database table lacks a declared PK, and because `idx IS NULL` is encoded in changesets as a zero-length blob.
- Streaming APIs are controlled by global `sessions_strm_chunk_size`, defaulting to `SESSIONS_STRM_CHUNK_SIZE` and configurable through `SQLITE_SESSION_CONFIG_STRMSIZE`.

## Risks and Edge Cases

- The binary format parser is corruption-sensitive. The code contains explicit bounds checks, maximum column sanity checks, safe varint reads, and `SQLITE_CORRUPT_BKPT` returns, but malformed varints, record lengths, undefined PK values, or truncated streaming input are core risk areas.
- Floating-point serialization has TODO notes about mixed-endian floating-point platforms. Integers are normalized big-endian, but doubles are copied from native representation before big-endian integer storage.
- NULL primary-key values are ignored during capture, while corrupt input may still contain them. Apply and changegroup validation must preserve the invariant that PK values are defined and non-NULL.
- Schema changes are nuanced. Adding columns with defaults is supported in several paths, but primary-key changes, hidden columns, rowid fallback, and mismatched column names or counts can produce `SQLITE_SCHEMA` or skipped apply tables.
- `sqlite_stat1` has bespoke NULL/blob handling and SQL generation. Tests must cover it separately from normal tables.
- Apply conflict behavior is complex and callback-driven. Incorrect callback return handling can lead to aborts, misuse errors, omitted changes, unexpected retries, or missing rebase records.
- Constraint retry logic buffers raw change bytes and replays them with iterator state synthesized from the current table. Ordering bugs here can surface only with interdependent constraints or UPDATEs that need delete/reinsert handling.
- Statement-cache allocation in `sessionUpdateFind()` uses a suspicious `sizeof(SessionUpdate) * nU32*sizeof(u32)` expression where an additive layout is expected; tests around many UPDATE column masks can guard this area.
- Memory ownership is mixed between `sqlite3_malloc`, `sessionMalloc64` with accounting, `sqlite3_value` allocation, prepared statements, and buffers handed to callers. OOM paths and finalize/reset ordering are important.
- Preupdate hooks run under the database mutex and mutate session state. Multiple sessions on one connection share the hook list and must be unlinked carefully.

## Test Signals

Strong test coverage should exercise:

- Basic capture for INSERT, UPDATE, DELETE on explicit and auto-attached tables.
- Tables without PKs, NULL PK components, composite PKs, INTEGER PRIMARY KEY aliases, WITHOUT ROWID tables, and implicit rowid PK mode.
- Changeset versus patchset output, including no-op UPDATE omission and indirect-change flags.
- Streaming generation, iteration, apply, inversion, concat, changegroup, and rebase with small chunk sizes.
- Corrupt changeset inputs: invalid table headers, oversized column counts, truncated text/blob payloads, invalid op/type bytes, undefined or NULL PK values, and malformed patchset DELETE records.
- Schema drift: columns added with defaults after capture, PK changes, hidden/generated columns from `table_xinfo`, and apply targets with fewer/mismatched columns.
- `sqlite_stat1` capture/apply with `idx` NULL and non-NULL values.
- Apply conflict callback modes for DATA, NOTFOUND, CONFLICT, CONSTRAINT, and FOREIGN_KEY, including OMIT, REPLACE, ABORT, and invalid callback returns.
- Deferred foreign-key and constraint retry behavior, especially update-loop delete/reinsert cases and `SQLITE_CHANGESETAPPLY_NOUPDATELOOP`.
- Rebase production from `apply_v2/v3` and later `sqlite3rebaser_rebase()` transformations for local INSERT/UPDATE/DELETE cases.
- OOM and allocation-accounting behavior for large records, many changes, large text/blob values, and many distinct UPDATE masks.
