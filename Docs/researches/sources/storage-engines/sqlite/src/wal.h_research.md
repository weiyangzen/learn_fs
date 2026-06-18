# sources/storage-engines/sqlite/src/wal.h

## Purpose

`wal.h` defines the internal interface between SQLite's pager and the write-ahead log implementation. It declares the opaque `Wal` handle, sync-flag extraction macros, savepoint data size, and all pager-facing WAL operations. It also supplies no-op macro substitutes when SQLite is compiled with `SQLITE_OMIT_WAL`.

## Important APIs, Types, and Functions

`WAL_SYNC_FLAGS(X)` extracts commit-sync flags from the low two bits of a combined sync flag word, while `CKPT_SYNC_FLAGS(X)` extracts checkpoint-sync flags from bits 2 and 3. `WAL_SAVEPOINT_NDATA` is `4`, matching the four `u32` values saved by `sqlite3WalSavepoint()` in `wal.c`.

The header forward-declares `typedef struct Wal Wal`, keeping the implementation private. Core lifecycle APIs are `sqlite3WalOpen()`, `sqlite3WalClose()`, and `sqlite3WalLimit()`. Reader APIs are `sqlite3WalBeginReadTransaction()`, `sqlite3WalEndReadTransaction()`, `sqlite3WalFindFrame()`, `sqlite3WalReadFrame()`, and `sqlite3WalDbsize()`. Writer APIs are `sqlite3WalBeginWriteTransaction()`, `sqlite3WalEndWriteTransaction()`, `sqlite3WalUndo()`, `sqlite3WalSavepoint()`, `sqlite3WalSavepointUndo()`, and `sqlite3WalFrames()`. Checkpoint and notification APIs are `sqlite3WalCheckpoint()` and `sqlite3WalCallback()`. Mode and inspection APIs are `sqlite3WalExclusiveMode()`, `sqlite3WalHeapMemory()`, and `sqlite3WalFile()`.

Feature-gated declarations expose `sqlite3WalSnapshotGet()`, `sqlite3WalSnapshotOpen()`, `sqlite3WalSnapshotRecover()`, `sqlite3WalSnapshotCheck()`, and `sqlite3WalSnapshotUnlock()` under `SQLITE_ENABLE_SNAPSHOT`; `sqlite3WalFramesize()` under `SQLITE_ENABLE_ZIPVFS`; `sqlite3WalWriteLock()` and `sqlite3WalDb()` under `SQLITE_ENABLE_SETLK_TIMEOUT`; and `sqlite3WalSystemErrno()` under `SQLITE_USE_SEH`.

## Control Flow

There is no executable control flow in this header, but the declarations describe the pager's WAL sequence. The pager opens a `Wal` object for a database file, begins and ends read transactions around page-cache access, asks whether a page has a visible WAL frame, reads that frame if present, upgrades a read transaction to a write transaction, writes dirty page frames, records or rolls back savepoints, checkpoints frames into the database, and closes the WAL on pager shutdown.

When `SQLITE_OMIT_WAL` is defined, the same call sites compile against macros returning benign defaults such as `SQLITE_OK`-like zero values, zero database size, and null WAL file pointers. This keeps WAL-free builds from needing alternate pager code for most calls.

## State and Persistence Behavior

The header itself stores no state. It defines the contract for state stored by `wal.c`: the opaque `Wal` object, reader snapshots, writer lock ownership, uncommitted frame positions, checkpoint progress, and WAL hook callback frame counts. Persistence effects are delegated to the implementation: frame writes to the `-wal` file, checkpoint writes to the database file, shared-memory wal-index updates, and possible WAL deletion or truncation on close.

`sync_flags` parameters deliberately combine commit and checkpoint sync policy in one integer. Callers must use the macros consistently so commits and checkpoint backfills use the correct VFS sync flags.

## Dependencies and Integration Points

`wal.h` includes `sqliteInt.h`, so it depends on SQLite internal types such as `sqlite3_vfs`, `sqlite3_file`, `sqlite3`, `PgHdr`, `Pgno`, `u8`, and `i64`. Its main consumer is the pager layer, with additional reach from public snapshot APIs and WAL-hook/checkpoint plumbing. `sqlite3WalFile()` exposes the WAL `sqlite3_file` for lower-level pager/VFS integration.

Compile-time flags shape the ABI visible inside SQLite. Builds without WAL get macro stubs and undefine `SQLITE_USE_SEH`; snapshot, ZIPVFS, blocking locks, and SEH declarations appear only when their feature macros are enabled.

## Risks and Edge Cases

Because this header is an internal boundary, signature drift between `wal.h` and `wal.c` would break pager integration. The no-op `SQLITE_OMIT_WAL` macros must preserve enough type and value compatibility that callers remain correct in WAL-free builds. `WAL_SAVEPOINT_NDATA` must match the implementation's savepoint payload exactly.

`sqlite3WalCheckpoint()` has many pointer and buffer parameters, so caller mistakes around `nBuf`, `zBuf`, or output pointers can surface as corruption checks or I/O errors in the implementation. Feature-gated declarations require call sites to be equally gated.

## Test Signals

Build tests should cover normal WAL-enabled builds, `SQLITE_OMIT_WAL`, snapshot-enabled builds, ZIPVFS builds, set-lock-timeout builds, and SEH builds where applicable. Pager-level tests should confirm the declared transaction sequence: begin read, find/read frame, begin write, frames, savepoint rollback, checkpoint, callback, exclusive mode transitions, and close. Compile-only tests are especially useful for the macro-stub path.
