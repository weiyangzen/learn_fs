# sources/storage-engines/sqlite/src/vdbeblob.c

## Purpose

`vdbeblob.c` implements SQLite's incremental BLOB I/O API when `SQLITE_OMIT_INCRBLOB` is not defined. It provides `sqlite3_blob_open()`, `sqlite3_blob_close()`, `sqlite3_blob_read()`, `sqlite3_blob_write()`, `sqlite3_blob_bytes()`, and `sqlite3_blob_reopen()`. The implementation opens a hidden VDBE program that owns transaction, locking, schema, and cursor lifetime, then lets the blob API borrow its btree cursor to read or write a fixed-size text/blob field in one row.

## Important APIs, types, and functions

- `Incrblob` is the private blob handle. It stores the opened value length (`nByte`), byte offset within the row record (`iOffset`), target column (`iCol`), borrowed btree cursor (`pCsr`), owning prepared statement (`pStmt`), database handle, database name, and table pointer.
- `blobSeekToRow(Incrblob*, sqlite3_int64, char**)` positions the hidden VDBE cursor on the requested rowid, validates that the target field is TEXT or BLOB, caches the field offset and byte length, and registers the cursor as an incremental-blob cursor with btree.
- `sqlite3_blob_open()` validates the table and column, rejects unsupported table shapes, rejects unsafe write targets, builds and prepares the hidden VDBE, seeks to the initial row, and returns the `Incrblob` as an opaque `sqlite3_blob*`.
- `sqlite3_blob_close()` frees the `Incrblob` wrapper under the database mutex, then finalizes the hidden statement, which closes the cursor and may commit or roll back the transaction according to normal VDBE rules.
- `blobReadWrite()` is the shared range-checking, mutex, cursor-enter, read/write, error-propagation, invalidation, and optional preupdate-hook path for `sqlite3_blob_read()` and `sqlite3_blob_write()`.
- `sqlite3_blob_read()` calls `blobReadWrite()` with `sqlite3BtreePayloadChecked`; `sqlite3_blob_write()` calls it with `sqlite3BtreePutData`.
- `sqlite3_blob_bytes()` returns the fixed opened value size while the statement remains valid.
- `sqlite3_blob_reopen()` retargets an existing handle to a different row in the same table/column by reusing `blobSeekToRow()`.

## Control flow

Opening begins by zeroing `*ppBlob`, entering `db->mutex`, allocating `Incrblob`, and initializing a stack `Parse`. The loop around `sqlite3LocateTable()` and `blobSeekToRow()` retries on `SQLITE_SCHEMA` up to `SQLITE_MAX_SCHEMA_RETRY`. The table must be a rowid ordinary table; virtual tables, WITHOUT ROWID tables, tables with generated columns, and views are rejected.

For write handles, `sqlite3_blob_open()` rejects columns that are part of a child foreign key when foreign keys are enabled, and rejects indexed columns. Expression indexes cause conservative rejection because the code cannot prove whether the expression depends on the target column. This preserves index and foreign-key consistency because incremental writes bypass normal SQL expression and constraint update machinery.

The hidden bytecode program starts with `OP_Transaction`, then a small `openBlob` program: optional `OP_TableLock`, `OP_OpenRead` or `OP_OpenWrite`, `OP_NotExists`, `OP_Column`, `OP_ResultRow`, and `OP_Halt`. The `OP_Column` reads an artificial column (`pTab->nCol`) to populate cursor type/offset cache without reading the actual payload. `sqlite3VdbeUsesBtree()` records btree usage for locking, and `sqlite3VdbeMakeReady()` packages the statement with one memory register and one cursor.

`blobSeekToRow()` writes the target rowid directly into VDBE register 1. On first use it calls `sqlite3_step()`. On reopen, if the VM is paused at `OP_ResultRow`, it moves `v->pc` back to the `OP_NotExists` opcode and calls `sqlite3VdbeExec()` directly. A successful row caches `pCsr`, `iOffset`, and `nByte`; a non-blob/text value or missing row finalizes the hidden statement, clears `pStmt`, and returns an error.

Reads and writes check null handle, negative sizes or offsets, and range overflow against the immutable `nByte`. A valid operation enters the btree cursor, calls the selected btree payload routine at `iOffset + p->iOffset`, leaves the cursor, stores the result in `v->rc`, and converts `SQLITE_ABORT` into permanent handle invalidation by finalizing the statement and setting `pStmt` to NULL.

## State and persistence behavior

The blob handle is valid only while `Incrblob.pStmt` is non-NULL. Errors from missing rows, wrong value type, btree aborts, or failed reopen invalidate the handle for future read/write/reopen calls, which then return `SQLITE_ABORT` until close.

The blob size is fixed for the lifetime of the opened row value. `sqlite3_blob_write()` can modify bytes in place but cannot grow or shrink the field. `sqlite3_blob_bytes()` deliberately needs no mutex because `nByte` is immutable after a successful seek, although it returns zero if the handle or hidden statement is invalid.

The hidden VDBE owns transaction and cursor persistence. Closing the blob finalizes the VDBE; if the blob was opened for writing, finalize/reset/halt logic in `vdbeaux.c` is responsible for committing, rolling back, invoking hooks, and releasing locks.

Btree invalidation protects against concurrent row deletion or movement. The cursor is registered with `sqlite3BtreeIncrblobCursor()`. If later btree operations invalidate it, read/write may receive `SQLITE_ABORT`; the handle then finalizes its statement and becomes permanently aborted.

When preupdate hooks are enabled, blob writes call `sqlite3VdbePreUpdateHook()` before writing, after restoring the cursor if necessary. The operation is reported as `SQLITE_DELETE` with `iBlobWrite` identifying the blob column, matching existing session/preupdate expectations in this code path.

## Dependencies and integration points

`vdbeblob.c` includes `sqliteInt.h` and `vdbeInt.h`. It depends on schema lookup (`sqlite3LocateTable`, `sqlite3ColumnIndex`, schema-to-index mapping), table metadata (`Table`, `Index`, `FKey`, generated/view/virtual/rowid flags), VDBE construction and finalization, btree cursor APIs, shared-cache table locks, transaction opcodes, memory/error APIs, mutex discipline, API armor, preupdate hooks, and public extension API tables.

It integrates with Tcl and C test wrappers in `test_blob.c`, `test1.c`, and `tclsqlite.c`, with btree invalidation logic for incremental blob cursors, with zeroblob-producing SQL functions and bind APIs, and with VDBE lifecycle code in `vdbeaux.c` for statement close/commit behavior.

Feature gates that change behavior include `SQLITE_OMIT_INCRBLOB`, `SQLITE_ENABLE_API_ARMOR`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_SHARED_CACHE`, and `SQLITE_ENABLE_PREUPDATE_HOOK`.

## Risks and edge cases

- `blobSeekToRow()` depends on hard-coded bytecode layout: it resets `v->pc` to opcode index 4 and asserts that the opcode is `OP_NotExists`. Changes to `openBlob` instruction order require coordinated updates.
- The hidden `OP_Column` deliberately uses an artificial column to populate offset/type caches. Changes to cursor header parsing could break incremental blob offset discovery.
- Write-safety checks are conservative but critical. Allowing writes to indexed, foreign-key, generated-column, view, virtual, or WITHOUT ROWID targets would bypass normal SQL maintenance paths.
- Range checking must avoid signed overflow; the code casts offset plus length through `sqlite3_int64` before comparing against `nByte`.
- `sqlite3_blob_close()` frees the wrapper before finalizing the statement. It saves `pStmt` first, so this is intentional, but any future close-time use of `Incrblob` fields after the free would be unsafe.
- Reopen after an error must not leave a half-valid cursor. The code asserts that failures leave `pStmt==0`.
- Preupdate hook semantics use `SQLITE_DELETE` for writes even though the logical operation is an update; consumers must understand this special case through `iBlobWrite`.
- Schema retry must reset parse state correctly on each attempt to avoid stale errors or leaked parse allocations.

## Test signals

Relevant tests include `test/incrblob*.test`, `test/e_blobopen.test`, `test/e_blobclose.test`, `test/e_blobwrite.test`, `test/savepoint.test`, `test/fkey2.test`, `test/fkey7.test`, `test/without_rowid*.test`, `test/tkt2332.test`, `test/corruptK.test`, and blob wrappers in `src/test_blob.c` and `src/test1.c`. Useful coverage signals are successful open/read/write/reopen/close, correct errors for missing rows and non-blob values, rejected writes to indexed or FK columns, correct behavior after row deletion/invalidation, correct readonly write failure, stable `sqlite3_blob_bytes()`, close with NULL handle returning OK, schema-change retry behavior, preupdate hook observations, and OOM/API-armor paths.
