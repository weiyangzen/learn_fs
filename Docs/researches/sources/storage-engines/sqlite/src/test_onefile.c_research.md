<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_onefile.c -->
# sources/storage-engines/sqlite/src/test_onefile.c

## Purpose
`test_onefile.c` is a demo/test VFS named `fs` that makes SQLite treat one fixed-size blob as embedded media containing both the main database and rollback journal. It demonstrates how a non-filesystem storage device could expose only block read/write/sync operations while still supporting SQLite pager semantics.

## Important APIs, Types, And Functions
The central types are `fs_vfs_t`, `fs_real_file`, `fs_file`, and `tmp_file`. `fs_register()` registers the VFS. `fsOpen()`, `fsRead()`, `fsWrite()`, `fsSync()`, `fsDelete()`, and `fsAccess()` implement the SQLite VFS and I/O methods. `tmp*()` methods back statement journals and other temporary files with heap memory. Constants `BLOCKSIZE` and `BLOBSIZE` define 512-byte sectors and a 10 MB simulated medium.

## Control Flow
Opening a main database creates or finds an `fs_real_file` backed by the parent VFS. A new parent file is extended to `BLOBSIZE`; an existing one reads the database size from the first four bytes and detects a possible journal by checking the last block. Main database offsets are translated by adding one block for the metadata header. Journal offsets are mapped backward from the end of the blob, block by block. Syncing the database writes the current database-region size into byte zero and then syncs the parent handle. Deleting the journal zeroes the first journal header area and clears volatile journal size.

## State And Persistence Behavior
Persistent state is the blob file itself: first block metadata, database content after block zero, and journal content growing backward from the end. `nDatabase` is persisted on database sync; `nJournal` is process-local and reconstructed conservatively after a crash. The VFS maintains an in-memory open-file list with reference counts. Temporary non-main files persist only in malloc-backed buffers.

## Dependencies And Integration Points
The file depends on SQLite VFS APIs and delegates path, dynamic loading, randomness, sleep, and time calls to the parent VFS. It is registered into testfixture through `SqlitetestOnefile_Init()` when `SQLITE_TEST` is enabled.

## Risks And Test Signals
Risks include no real locking, one-connection assumptions, fixed 10 MB capacity, journal-size reconstruction that intentionally over-reports after crash, no WAL/shared-memory support, and reliance on rollback-journal recovery checksums to ignore garbage past the logical journal end. Test signals include creating and reopening a database through `vfs=fs`, rollback after simulated crash with a nonzero journal tail, `SQLITE_FULL` when database and journal regions collide, zeroed journal header after delete, and temp objects staying in memory.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_onefile.c -->
