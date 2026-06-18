# sources/storage-engines/sqlite/src/wal.c

## Purpose

`wal.c` implements SQLite's write-ahead log subsystem for `journal_mode=WAL`. It owns the on-disk `-wal` format, the transient shared-memory `-shm` wal-index, read snapshots, single-writer enforcement, checkpoint backfill into the main database, WAL reset/truncation, optional snapshot APIs, optional blocking-lock timeout support, and Windows SEH handling for faults while touching memory-mapped shared memory.

The file is excluded when `SQLITE_OMIT_WAL` is defined. Otherwise it is the implementation behind the pager-facing APIs declared in `wal.h`.

## Important APIs, Types, and Functions

The central type is `struct Wal`, which binds the database file, WAL file, VFS, shared-memory pages, cached `WalIndexHdr`, current read/write/checkpoint lock state, page size, salts, callback frame number, size limits, and feature-specific fields for SEH, snapshots, and set-lock timeouts. `WalIndexHdr` is the duplicated shared-memory header containing WAL format version, change counter, page size, `mxFrame`, database page count, frame checksums, salts, and header checksum. `WalCkptInfo` follows the two headers in shared memory and stores `nBackfill`, `nBackfillAttempted`, reader marks, and reserved lock bytes. `WalIterator` is a checkpoint helper that merges wal-index segments in page-number order while keeping only the latest frame per database page.

Public entry points include `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalLimit()`, `sqlite3WalBeginReadTransaction()`, `sqlite3WalEndReadTransaction()`, `sqlite3WalFindFrame()`, `sqlite3WalReadFrame()`, `sqlite3WalDbsize()`, `sqlite3WalBeginWriteTransaction()`, `sqlite3WalEndWriteTransaction()`, `sqlite3WalUndo()`, `sqlite3WalSavepoint()`, `sqlite3WalSavepointUndo()`, `sqlite3WalFrames()`, `sqlite3WalCheckpoint()`, `sqlite3WalCallback()`, `sqlite3WalExclusiveMode()`, `sqlite3WalHeapMemory()`, `sqlite3WalFile()`, and feature-gated snapshot, ZIPVFS, SEH, and blocking-lock functions.

Important private routines fall into clear groups. Format and checksum helpers include `walFrameOffset()`, `walChecksumBytes()`, `walEncodeFrame()`, `walDecodeFrame()`, and `walPagesize()`. Shared-memory helpers include `walIndexPage()`, `walIndexPageRealloc()`, `walIndexHdr()`, `walCkptInfo()`, `walIndexWriteHdr()`, `walIndexTryHdr()`, and `walIndexReadHdr()`. Hash/index routines include `walHashGet()`, `walFramePage()`, `walFramePgno()`, `walCleanupHash()`, `walIndexAppend()`, and `walIndexRecover()`. Locking routines include `walLockShared()`, `walUnlockShared()`, `walLockExclusive()`, `walUnlockExclusive()`, and `walBusyLock()`. Checkpoint traversal is implemented by `walIteratorInit()`, `walIteratorNext()`, `walMerge()`, `walMergesort()`, and `walCheckpoint()`. Write sequencing is implemented by `walRestartLog()`, `walWriteToLog()`, `walWriteOneFrame()`, `walRewriteChecksums()`, and `walFrames()`.

## Control Flow

Opening starts in `sqlite3WalOpen()`, which verifies WAL layout constants, allocates `Wal` plus an embedded `sqlite3_file`, opens the `-wal` file, records read-only state, configures sync/header-padding behavior from VFS device characteristics, and chooses normal shared-memory mode or heap wal-index mode for `bNoShm`.

Read transactions run through `sqlite3WalBeginReadTransaction()`, which wraps `walBeginReadTransaction()` in SEH where enabled. `walBeginReadTransaction()` repeatedly calls `walTryBeginRead()` until transient `WAL_RETRY` races settle or a protocol limit is reached. `walTryBeginRead()` loads or recovers the wal-index header, handles unreliable read-only shared memory by falling back to heap reconstruction, decides whether the WAL can be ignored via read-lock 0, or selects a reader mark not greater than the snapshot's `mxFrame`. After acquiring the shared read lock, it rechecks both the reader mark and the live header so a concurrent writer/checkpointer cannot make the cached snapshot unsafe. Reads then use `sqlite3WalFindFrame()` to search wal-index hash blocks from newest to oldest between `minFrame` and `mxFrame`; if a frame is found, `sqlite3WalReadFrame()` reads page content from the WAL file.

Write transactions require an existing read transaction. `sqlite3WalBeginWriteTransaction()` acquires `WAL_WRITE_LOCK` and rejects the write with `SQLITE_BUSY_SNAPSHOT` if the live wal-index header differs from the reader's cached header, preventing forked WAL histories. `sqlite3WalFrames()` writes dirty pages via `walFrames()`: it may reset the log if everything is checkpointed and no reader uses WAL frames, writes a new WAL header when starting from frame 1, appends or overwrites frames, handles commit markers through `nTruncate`, syncs according to `sync_flags`, pads to sector boundaries when needed, optionally limits WAL size, appends mapping entries to the wal-index, and publishes a new wal-index header on commit. `sqlite3WalEndWriteTransaction()` releases the writer lock and clears transient checksum/truncation state.

Rollback and savepoint flow is local to wal-index state. `sqlite3WalUndo()` restores the cached header from shared memory, invokes the pager callback for uncommitted frames, and prunes hash entries beyond the restored `mxFrame`. `sqlite3WalSavepoint()` captures `mxFrame`, frame checksums, and checkpoint counter; `sqlite3WalSavepointUndo()` restores those values and cleans the hash when rolling back to a savepoint, including the special case where the WAL was restarted after the savepoint was opened.

Checkpoint flow starts in `sqlite3WalCheckpoint()`, which obtains the checkpoint lock, optionally obtains the writer lock for FULL/RESTART/TRUNCATE modes, reads the wal-index header, validates page size against the caller's buffer, and calls `walCheckpoint()`. `walCheckpoint()` computes the maximum frame safe to backfill by inspecting reader marks, builds a `WalIterator`, syncs the WAL, hints database growth, copies the latest applicable frame for each database page into the database file, truncates and syncs the database if fully checkpointed, updates `nBackfill`, and for RESTART/TRUNCATE waits for WAL readers before resetting the header or truncating the WAL.

Recovery flow is driven by `walIndexReadHdr()` when the wal-index header is missing, dirty, corrupt, or uninitialized. It obtains the write lock, calls `walIndexRecover()`, reads the WAL header, validates magic/page-size/version/checksum/salts, scans frames until the first invalid frame, appends valid frame mappings, records the last commit frame as `mxFrame`, writes the rebuilt wal-index header, resets checkpoint metadata, initializes read marks, and logs recovery when frames were found.

## State and Persistence Behavior

Persistent state lives in the main database file and `-wal` file. The WAL header is 32 bytes and stores magic, version, page size, checkpoint sequence, salts, and checksum. Each frame has a 24-byte header with page number, commit database size or zero, salts, and rolling checksums, followed by page data. A transaction commits only when a frame with nonzero database size is written and later published through the wal-index header.

The wal-index is transient shared memory, normally backed by the `-shm` file. It is native-endian and can be rebuilt from the WAL after a crash. Its duplicated header uses a checksum and memory barriers to detect dirty reads; writers copy header copy 1 then copy 0, while readers read copy 0 then copy 1. Hash blocks map page numbers to frame indexes so readers can find the newest visible frame without scanning the WAL file.

Lock state is shared through VFS `xShmLock` slots at fixed offsets: write, checkpoint, recovery, and multiple read locks. `aReadMark[]` entries bound each reader's view, while `nBackfill` and `nBackfillAttempted` coordinate checkpoint progress and snapshot validity. Read-lock 0 means the reader ignores the WAL and reads only the database file.

Durability depends on the sync mode. WAL commits may sync the WAL and may pad transactions to sector boundaries. Checkpoints sync the WAL before copying pages and sync the database when the entire WAL is backfilled. WAL reset increments/checks salts to keep old frames from being mistaken for current content after reuse. Close may checkpoint and delete or truncate persistent WAL files depending on exclusive lock acquisition, persistent-WAL file-control result, and journal size limit.

## Dependencies and Integration Points

`wal.c` depends on `wal.h` and the broader SQLite internal layer from `sqliteInt.h`: VFS I/O (`sqlite3OsOpen`, `sqlite3OsRead`, `sqlite3OsWrite`, `sqlite3OsSync`, `sqlite3OsShmMap`, `sqlite3OsShmLock`, `sqlite3OsShmBarrier`, `sqlite3OsShmUnmap`, file-control hints), memory allocation, random salts, atomics, byte-order helpers, pager page headers, SQLite result codes, test macros, and logging. The pager uses this module for WAL-mode read/write transaction boundaries, page lookup, frame writes, rollback, checkpoint, close, and WAL hook callbacks.

The implementation is tightly coupled to VFS shared-memory semantics and lock-byte layout. It asserts compatibility with Unix and Windows shared-memory lock offsets and handles read-only WAL or read-only SHM cases explicitly. Compile-time features add integration points for `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_ENABLE_ZIPVFS`, `SQLITE_ENABLE_SETLK_TIMEOUT`, `SQLITE_USE_SEH`, `SQLITE_TEST`, and `SQLITE_DEBUG`.

## Risks and Edge Cases

The highest-risk behavior is concurrency across processes. Correctness depends on fixed lock ordering, atomic 32-bit shared-memory loads/stores, barriers around duplicated headers, retry loops for transient races, and conservative handling when a header changes between observation and lock acquisition. Breaking any of these can expose corrupt snapshots, forked histories, or unsafe checkpoint backfill.

Crash recovery and persistence are also delicate. Header checksums, frame rolling checksums, salts, checkpoint counters, and WAL reset logic must agree. A missed checksum rewrite after overwriting frames, an incorrect `minFrame`, or an unsafe `nBackfill` update can make readers fetch the wrong page version. The code has several defensive corruptions checks, including page-size validation, WAL version validation, hash collision bounds, and database growth sanity checks during checkpoint.

Read-only and unreliable-shared-memory paths are specialized and easy to regress. `SQLITE_READONLY_CANTINIT`, heap wal-index reconstruction, retry when a writer fixes shared memory, and salt/frame checks are all necessary to avoid reading a stale WAL image. Snapshot APIs add another layer: snapshots are invalid if salts change or if a checkpoint has attempted frames beyond the snapshot.

Platform feature paths carry specific risk. Windows SEH must release transient locks and restore heap/shared-memory bookkeeping after in-page errors. Blocking-lock timeout builds must normalize `SQLITE_BUSY_TIMEOUT` and avoid unintended long waits in passive checkpoints. ZIPVFS relies on frame-size reporting under a live read lock.

## Test Signals

Strong tests should exercise concurrent readers and writers with snapshot isolation, `SQLITE_BUSY_SNAPSHOT` when a reader tries to upgrade after another writer commits, passive/full/restart/truncate checkpoints with active readers, WAL reset only after all frames are backfilled and no WAL readers remain, rollback and savepoint undo across appended and overwritten frames, WAL recovery after simulated crashes at header/frame/index-update boundaries, and read-only WAL/SHM cases.

Existing in-file signals include TH3/testcase annotations for corrupt page sizes, large offsets, checkpoint busy-handler requirements, WAL format assertions, `sqlite3FaultSim()` hooks for allocation and shared-memory faults, expensive assertions that compare hash lookup with linear search, and debug WAL tracing. Tests should cover sync modes, persistent WAL deletion/truncation policy, journal size limit, snapshot get/open/check/recover, SEH in-page-error handling where enabled, and set-lock timeout behavior.
