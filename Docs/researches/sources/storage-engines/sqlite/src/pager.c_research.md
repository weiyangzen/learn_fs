# Research: sources/storage-engines/sqlite/src/pager.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008779`: lines 1-6685, `Docs/researches/chunks/subset-b-008779_research.md`
- `subset-b-008780`: lines 6686-7828, `Docs/researches/chunks/subset-b-008780_research.md`

## Chunk Research

### subset-b-008779: lines 1-6685

# sources/storage-engines/sqlite/src/pager.c lines 1-6685

## Chunk Scope

This chunk covers the first 6685 lines of SQLite's pager implementation. It includes the pager state model, rollback-journal format and playback, WAL read/write handoffs, page-cache integration, pager construction/destruction, shared-lock acquisition, page fetch/release APIs, page journaling/writeability, and the first phase of commit. The chunk stops inside the comment for `sqlite3PagerCommitPhaseTwo()`, so transaction finalization, rollback public APIs, savepoint public APIs, journal-mode switching, page move/rekey helpers, and WAL open/close/snapshot tail functions are cross-chunk continuation points.

## Purpose

The pager is the storage layer that turns database pages into durable, transactional file operations. It sits between btree/page users and the VFS/pcache/WAL subsystems, enforcing the invariants needed for atomic commit and rollback. For rollback-journal mode it writes original page images to a separate journal before overwriting database pages, detects and replays hot journals, coordinates super-journals for multi-database commits, and updates database header change counters. For WAL mode it delegates concurrency and persistence to `wal.c`, while still owning page cache state, savepoint interactions, backup notifications, mmap fetches, and transaction state.

The large design comment at the top is part of the contract: database pages are not overwritten until safely journaled or otherwise overwriteable; database writes are page-aligned; journal/database sync ordering protects rollback; exclusive locks guard database writes; shared locks guard reads; and bytes 24..39 of page 1 are used as cache invalidation/version evidence.

## Important Types, State, and Constants

- `Pager` is the central object. Its configuration fields include VFS/file handles, journal mode, sync policy, temp/memory/read-only flags, page size/reserve bytes, sector size, mmap limit, busy handler, and WAL pointers. Its mutable state includes `eState`, `eLock`, `dbSize`, `dbOrigSize`, `dbFileSize`, `dbHintSize`, `errCode`, `journalOff`, `journalHdr`, `nRec`, `pInJournal`, `aSavepoint`, `iDataVersion`, `dbFileVers`, mmap outstanding counts, and the PCache pointer.
- Pager states are `PAGER_OPEN`, `PAGER_READER`, `PAGER_WRITER_LOCKED`, `PAGER_WRITER_CACHEMOD`, `PAGER_WRITER_DBMOD`, `PAGER_WRITER_FINISHED`, and `PAGER_ERROR`. The normal rollback path is open/shared read, writer lock, cache modification after journal creation, database modification after journal sync, and finished after phase-one commit. WAL never enters DBMOD or FINISHED.
- `UNKNOWN_LOCK` records a conservative lock state after an unlock failure from error recovery, forcing later hot-journal handling to assume risk rather than trusting `xCheckReservedLock()`.
- `PagerSavepoint` arrays and bitvecs track savepoint boundaries and which pages have been captured in the sub-journal.
- `aJournalMagic`, `JOURNAL_PG_SZ()`, and `JOURNAL_HDR_SZ()` define rollback journal record/header layout. Journal records are page number, page data, and checksum; headers contain magic, record count, checksum seed, original database size, sector size, and page size.
- `MEMDB` and `USEFETCH` compile-time/runtime macros gate in-memory databases and mmap `xFetch()` access.

## Important APIs and Functions

- Diagnostics and state guards: `assert_pager_state()` validates state/lock/file/cache invariants in debug builds. `print_pager_state()` formats pager internals for debugger use.
- File integer helpers: `read32bits()`, `write32bits()`, and `put32bits` encode journal fields as big-endian values.
- Lock wrappers: `pagerLockDb()`, `pagerUnlockDb()`, and `pager_wait_on_lock()` centralize VFS lock transitions and busy-handler retry behavior.
- Journal format helpers: `journalHdrOffset()`, `writeJournalHdr()`, `readJournalHdr()`, `zeroJournalHdr()`, `readSuperJournal()`, `writeSuperJournal()`, and `pager_cksum()` construct, parse, invalidate, and validate rollback-journal data.
- Transaction cleanup/error paths: `pager_end_transaction()`, `pager_unlock()`, `pager_error()`, `pagerUnlockAndRollback()`, `pager_reset()`, and `pager_truncate()` release savepoints, finalize journals, drop locks, discard stale cache, enter/leave error state, and resize the database file.
- Rollback playback: `pager_playback_one_page()`, `pager_playback()`, `pagerPlaybackSavepoint()`, and `pager_delsuper()` restore pages from main journals/sub-journals and clean up super-journals once all child journals are safe.
- WAL integration: `pagerBeginReadTransaction()`, `pagerRollbackWal()`, `pagerUndoCallback()`, `pagerWalFrames()`, `pagerOpenWalIfPresent()`, and `sqlite3PagerDirectReadOk()` bridge pager state/cache behavior to WAL snapshots, WAL undo, WAL frame writes, and direct overflow reads.
- Page and cache APIs: `sqlite3PagerGet()`, `getPageNormal()`, `getPageMMap()`, `getPageError()`, `sqlite3PagerLookup()`, `sqlite3PagerUnref*()`, `sqlite3PagerSetCachesize()`, `sqlite3PagerSetSpillsize()`, `sqlite3PagerSetMmapLimit()`, and `sqlite3PagerShrink()` provide page fetch/release and cache tuning behavior.
- Pager lifecycle and metadata: `sqlite3PagerOpen()`, `sqlite3PagerClose()`, `sqlite3PagerSetFlags()`, `sqlite3PagerSetBusyHandler()`, `sqlite3PagerSetPagesize()`, `sqlite3PagerReadFileheader()`, `sqlite3PagerPagecount()`, `sqlite3PagerDataVersion()`, `sqlite3PagerTempSpace()`, `sqlite3PagerMaxPageCount()`, `sqlite3PagerPagenumber()`, and `sqlite3_database_file_object()`.
- Write path: `sqlite3PagerSharedLock()`, `sqlite3PagerBegin()`, `pager_open_journal()`, `pagerAddPageToRollbackJournal()`, `pager_write()`, `pagerWriteLargeSector()`, `sqlite3PagerWrite()`, `subjournalPage()`, `pagerStress()`, `sqlite3PagerFlush()`, `sqlite3PagerDontWrite()`, `pager_incr_changecounter()`, `syncJournal()`, `pager_write_pagelist()`, `sqlite3PagerSync()`, `sqlite3PagerExclusiveLock()`, and `sqlite3PagerCommitPhaseOne()` implement read-lock acquisition, write transaction start, page journaling, cache spill, dirty-page flush, and phase-one commit durability.

## Control Flow

Opening a pager with `sqlite3PagerOpen()` computes canonical paths and adjacent journal/WAL names, allocates one contiguous block for `Pager`, PCache, VFS file handles, filename strings, and journal names, opens the database if non-temporary, chooses defaults from sector/device characteristics, sets the page size and PCache, initializes journal mode and sync policy, and installs the page getter method. Temporary, immutable, and memory-like databases are treated as already locked/exclusive where appropriate.

Reads begin through `sqlite3PagerSharedLock()`. In rollback mode, the pager obtains a SHARED lock from OPEN, checks for a hot journal with `hasHotJournal()`, escalates directly to EXCLUSIVE if recovery is required, opens/syncs/replays the journal with `pager_playback()`, then validates the cached file-version bytes and discards cache/mmap mappings if another connection changed the file. It then opens WAL mode if a WAL file is present. In WAL mode it starts a WAL read transaction and resets cache if the snapshot changed. Finally it determines `dbSize` and enters READER.

Page fetches dispatch through `pPager->xGet`. `getPageNormal()` returns cached pages when possible, otherwise allocates/fetches from PCache, zero-fills pages beyond `dbSize` or requested with `PAGER_GET_NOCONTENT`, or reads from database/WAL via `readDbPage()`. `getPageMMap()` uses VFS `xFetch()` for eligible read-only pages outside page 1, falling back to normal fetch if WAL contains the page, mmap is unavailable, or a writable/cache copy is needed. `getPageError()` returns the stored persistent pager error.

Writes start with `sqlite3PagerBegin()`. Rollback mode obtains RESERVED or EXCLUSIVE locks and records `dbOrigSize`, `dbFileSize`, and `dbHintSize`; WAL mode begins the WAL write transaction and optionally acquires an exclusive database lock for exclusive-mode connections. The first page modification calls `sqlite3PagerWrite()`, which opens/writes the rollback journal header through `pager_open_journal()` if still in WRITER_LOCKED. `pager_write()` marks the page dirty only after the journal path is ready, journals original page content if the page existed at transaction start, marks append pages as needing sync where required, sets `PGHDR_WRITEABLE` only after safe journaling, records savepoint sub-journal content if needed, and expands `dbSize`.

Dirty cache spill is handled by `pagerStress()`. It refuses to spill during rollback, user-disabled spill, no-sync-sensitive windows, or error state. In WAL mode it sub-journals for savepoints then emits a single WAL frame. In rollback mode it creates the journal if batch-atomic support requires it, syncs the journal before database writes when `PGHDR_NEED_SYNC` or still CACHEMOD, writes the page list to the database, and marks the page clean only on success.

Rollback and recovery use `pager_playback()` and `pager_playback_one_page()`. The main playback loop reads journal headers, uses the journal record count unless no-sync/safe-append rules require deriving it from file size, truncates the database to the original size on the first header, then replays page records. A replayed page may update only cache, update both cache and database, or be skipped if out of range/already done. Savepoint rollback uses a `Bitvec` to avoid duplicate restores across main journal segments and the sub-journal, and WAL savepoint rollback delegates to `sqlite3WalSavepointUndo()`.

Phase-one commit through `sqlite3PagerCommitPhaseOne()` is the durable write phase. WAL mode writes dirty pages as WAL frames with a commit mark, creating a page-1 frame if needed so the commit can be represented. Rollback mode updates the change counter, writes a super-journal pointer if supplied, syncs the rollback journal, writes dirty pages to the database, grows/truncates the file image if needed, and syncs the database unless `noSync` is requested. On success, non-WAL mode enters `PAGER_WRITER_FINISHED`; final journal deletion/truncation is intentionally left to phase two outside this chunk.

## State and Persistence Behavior

The pager treats `dbSize` as the current logical database image, `dbOrigSize` as the size at write-transaction start, and `dbFileSize` as the known on-disk page count. `dbHintSize` throttles size-hint file-control calls. Page 1 bytes 24..39 are cached in `dbFileVers` and used to invalidate cache after locks are reacquired.

Rollback-journal persistence depends on strict ordering: original pages are written to the journal before they are made writable; journal data is synced before database overwrites; database data is synced before the journal is finalized; and hot journals are synced before playback so repeated crash recovery sees stable recovery input. `PGHDR_NEED_SYNC` is the page-local marker that database writes must not occur until the relevant journal content is durable.

Journal modes alter finalization and storage: MEMORY journals are closed; TRUNCATE journals are truncated; PERSIST journals zero the first header unless a super-journal pointer or temp behavior requires truncation; DELETE journals are closed and deleted; OFF skips rollback-journal protection; WAL routes writes to the log instead of directly modifying the database file during the transaction.

Savepoints persist original page images in the sub-journal when a page might need to roll back to the savepoint state rather than transaction start. `PagerSavepoint.pInSavepoint` bitvecs prevent duplicate sub-journal records, while `iOffset`, `iHdrOffset`, and `iSubRec` delimit replay ranges.

Error state is intentionally sticky for I/O and full errors that may leave cache inconsistent. Major page APIs return `errCode` until all references are dropped and `pager_unlock()` can discard cache, reset mmap fetches, and return to OPEN. In-memory pagers cannot enter this persistent error state.

## Dependencies and Integration Points

- VFS/OS integration goes through `sqlite3OsOpen`, `Read`, `Write`, `Sync`, `Truncate`, `FileSize`, `Lock`, `Unlock`, `Access`, `Delete`, `FileControl`, `xFetch`, and `xUnfetch`. Device characteristics such as safe append, sequential writes, powersafe overwrite, atomic write, batch atomic write, immutable files, and undeletable-open files materially change pager behavior.
- PCache integration goes through `sqlite3PcacheOpen`, `Fetch`, `FetchStress`, `FetchFinish`, `MakeDirty`, `MakeClean`, `DirtyList`, `CleanAll`, `ClearWritable`, `Truncate`, `Clear`, `Ref`, and reference-count queries.
- WAL integration goes through `sqlite3WalBeginReadTransaction`, `sqlite3WalBeginWriteTransaction`, `sqlite3WalFrames`, `sqlite3WalFindFrame`, `sqlite3WalReadFrame`, `sqlite3WalUndo`, `sqlite3WalSavepointUndo`, `sqlite3WalDbsize`, `sqlite3WalClose`, `sqlite3WalEndReadTransaction`, and `sqlite3WalEndWriteTransaction`.
- Backup integration uses `sqlite3BackupUpdate()` when pages are restored/written and `sqlite3BackupRestart()` when cache-wide invalidation or WAL rollback makes incremental backup state stale.
- Btree integration is implied by page APIs and comments: btree calls shared-lock acquisition before fetching, holds page 1 until transaction/read end, uses `sqlite3PagerWrite()` before mutating page memory, reads headers with `sqlite3PagerReadFileheader()`, and uses `sqlite3PagerDontWrite()` for freelist leaf optimization.
- Compile-time feature flags (`SQLITE_OMIT_WAL`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_TEST`, `SQLITE_CHECK_PAGES`) change substantial paths and test-only counters/assertions.

## Risks and Edge Cases

- Lock-state conservatism is critical. Mishandling `UNKNOWN_LOCK` or direct SHARED-to-EXCLUSIVE hot-journal recovery can let another connection read a database before recovery or misclassify a hot journal.
- Journal header parsing must reject invalid sector/page sizes and corrupted magic/checksums without replaying garbage. The chunk contains several crash-window comments where using file size instead of `nRec`, or failing to zero a stale persistent-journal header, could corrupt a database after power loss.
- `PGHDR_NEED_SYNC`, `SPILLFLAG_NOSYNC`, and large-sector journaling are subtle. If pages sharing a physical sector are not all journaled and marked consistently, a torn sector write can invalidate rollback.
- `pagerStress()` can be invoked from memory pressure during otherwise read-like operations inside a transaction. Its errors call `pager_error()` because returning an I/O error without rollback would leave dirty cache and database state ambiguous.
- `sqlite3PagerDontWrite()` is deliberately disallowed for temp files and savepoints. Using it when original content may be needed for rollback would lose restore data.
- Super-journal cleanup reads child journal files and only deletes the super-journal when no live child still points to it. False deletion can break multi-file atomicity; false retention leaves harmless stale files.
- Mmap fetches must never serve page 1 and must be unfetched when cache invalidation or external truncate/extend cycles may make mappings stale.
- `sqlite3_database_file_object()` depends on the exact filename memory layout created by `sqlite3PagerOpen()`, and comments note external software depends on this layout. Any allocation-format refactor has compatibility risk.
- Batch-atomic and atomic-write paths rely on VFS file-control semantics. Failure fallback must recreate a journal or roll back atomic-write state correctly.

## Test Signals

- Debug builds should exercise `assert_pager_state()` across every state transition: OPEN->READER, READER->WRITER_LOCKED, journal open to CACHEMOD, journal sync to DBMOD, phase-one commit to FINISHED, error entry, and unlock recovery.
- Crash-recovery tests should cover hot journals with valid and invalid headers, no-sync `0xffffffff` record counts, persistent journals containing stale trailing headers, super-journal presence/absence, short reads, checksum mismatch, and recovery after sync/write/truncate failures.
- Locking tests should cover busy-handler retry only for NO_LOCK->SHARED and RESERVED->EXCLUSIVE, not SHARED->RESERVED or hot-journal SHARED->EXCLUSIVE.
- Savepoint tests should cover repeated modifications to the same page, pages beyond original size, sub-journal rollback after page movement, and WAL savepoint undo.
- Cache-spill tests should simulate memory pressure with `PGHDR_NEED_SYNC`, disabled spill, rollback spill inhibition, temp-file thresholds, and I/O errors from `pagerStress()`.
- WAL tests should cover read snapshot changes resetting cache, WAL commit with no dirty pages requiring page 1, WAL rollback reloading referenced pages, and backup restart/update notifications.
- Mmap tests should cover `xFetch()` success/fallback, page 1 exclusion, cache invalidation after file-version changes, and release of outstanding mmap headers on close.
- Compile-time matrix tests should include `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_OMIT_WAL`, mmap disabled/enabled, `SQLITE_CHECK_PAGES`, and `SQLITE_TEST` I/O fault simulation (`sqlite3FaultSim(400)` and simulated I/O disable/enable regions).

## Cross-Chunk Continuation Notes

Line 6685 ends before the implementation of `sqlite3PagerCommitPhaseTwo()`. The next chunk should connect this phase-one durable state to journal finalization, public rollback, savepoint opening/release/rollback APIs, page move/rekey operations, journal-mode transitions, and the remaining WAL management/snapshot APIs. It should also verify how `pager_end_transaction()` is invoked after successful phase two and how `pager_error()` is applied when finalization fails.

### subset-b-008780: lines 6686-7828

# sources/storage-engines/sqlite/src/pager.c lines 6686-7828

## Scope

This chunk covers the public tail of SQLite's pager implementation. It starts at commit phase two and rollback, continues through pager observability helpers, savepoint creation and rollback/release, filename/file-handle accessors, auto-vacuum page relocation helpers, journal and locking mode configuration, backup/cache hooks, and finishes with WAL checkpoint/open/close/snapshot adapter functions. These lines are the boundary where the btree, VDBE pragma, backup, WAL, snapshot, and test layers call into pager state that was built by earlier transaction, journaling, playback, and cache-spill code in the same file.

## Purpose

- Finalize committed rollback-journal transactions so their journals cannot later be interpreted as hot journals.
- Roll back active write transactions in rollback mode or WAL mode and make errors persistent when pager cache contents can no longer be trusted.
- Expose pager metadata used by higher layers: read-only status, cache statistics, memory use, page refcounts, filenames, VFS/file handles, journal name, journal mode, locking mode, backup pointer, and memory/temp-database classification.
- Manage savepoint state with `PagerSavepoint` records, main-journal offsets, sub-journal record counts, per-savepoint page bitvecs, and WAL savepoint cookies.
- Move dirty pages between page numbers for auto-vacuum and btree reorganization while preserving rollback and `PGHDR_NEED_SYNC` guarantees.
- Switch journal modes and locking modes under the restrictions required by temp databases, memory databases, persistent journals, and WAL shared-memory support.
- Provide WAL-facing adapters for checkpoints, WAL file open/close, write-lock routing under blocking-lock builds, snapshots, ZipVFS frame sizing, and platform error reporting.

## Important APIs, Types, And Functions

- `sqlite3PagerCommitPhaseTwo(Pager *pPager)` finalizes a transaction after phase one has made database/WAL content durable enough for commit. It increments `iDataVersion`, handles a persistent-journal exclusive-mode no-op case, delegates normal finalization to `pager_end_transaction(..., bCommit=1)`, and persists IO errors through `pager_error()`.
- `sqlite3PagerRollback(Pager *pPager)` aborts an active write transaction. It is a no-op in `PAGER_OPEN`/`PAGER_READER`, returns `errCode` directly in `PAGER_ERROR`, uses savepoint rollback plus `pager_end_transaction()` for WAL, uses `pager_playback()` when a rollback journal exists, and enters `PAGER_ERROR` with `SQLITE_ABORT` for non-memory `journal_mode=off` cases where cache changes cannot be restored.
- `sqlite3PagerIsreadonly()`, `sqlite3PagerIsMemdb()`, `sqlite3PagerMemUsed()`, `sqlite3PagerPageRefcount()`, `sqlite3PagerCacheStat()`, and test/debug-only `sqlite3PagerRefcount()`/`sqlite3PagerStats()` expose pager/cache state without mutating persistence.
- `PagerSavepoint` is the savepoint state carrier from earlier in the file: `iOffset` and `iHdrOffset` locate main-journal rollback ranges, `nOrig` restores the database image size, `iSubRec` locates sub-journal records, `pInSavepoint` tracks pages already captured for that savepoint, `bTruncateOnRelease` controls in-memory sub-journal trimming, and `aWalData[]` stores WAL-layer savepoint state when WAL is enabled.
- `pagerOpenSavepoint()` and `sqlite3PagerOpenSavepoint()` grow `Pager.aSavepoint[]`, initialize each new savepoint from current `dbSize`, `journalOff`, and `nSubRec`, allocate page bitvecs, and capture WAL savepoint data.
- `sqlite3PagerSavepoint(Pager *pPager, int op, int iSavepoint)` releases or rolls back a savepoint. It frees destroyed savepoint bitvecs, updates `nSavepoint`, truncates in-memory sub-journals on release, and invokes `pagerPlaybackSavepoint()` for rollback.
- `sqlite3PagerFilename()`, `sqlite3PagerVfs()`, `sqlite3PagerFile()`, `sqlite3PagerJrnlFile()`, and `sqlite3PagerJournalname()` are accessors used by btree, shared-cache matching, URI helpers, diagnostics, backup/VFS logic, and journaling pragmas.
- `sqlite3PagerMovepage()` is compiled when auto-vacuum is enabled. It moves a referenced dirty page to a new page number, handles the page already cached at the target number, sub-journals moved content when savepoints require it, and preserves `PGHDR_NEED_SYNC` obligations across the move.
- `sqlite3PagerRekey()`, `sqlite3PagerGetData()`, and `sqlite3PagerGetExtra()` are compact pcache-facing helpers for changing a dirty page's key and exposing its page payload/extra allocation.
- `sqlite3PagerLockingMode()` toggles/query normal versus exclusive locking mode, but refuses to change temp-file pagers or WAL heap-index users where exclusive mode is already tied to WAL internals.
- `sqlite3PagerSetJournalMode()`, `sqlite3PagerGetJournalMode()`, `sqlite3PagerOkToChangeJournalMode()`, and `sqlite3PagerJournalSizeLimit()` implement pager-side journal-mode state, cleanup of old persistent/truncate journals, and propagation of size limits to WAL.
- `sqlite3PagerBackupPtr()` exposes `Pager.pBackup` as an opaque pointer slot maintained by `backup.c`; the pager itself uses that list through `sqlite3BackupRestart()` and `sqlite3BackupUpdate()` in surrounding commit/playback/write paths.
- `sqlite3PagerClearCache()` clears purgeable pager cache content for vacuum-like callers, excluding temp/in-memory database images.
- WAL functions in this chunk include `sqlite3PagerCheckpoint()`, `sqlite3PagerWalCallback()`, `sqlite3PagerWalSupported()`, internal `pagerExclusiveLock()` and `pagerOpenWal()`, public `sqlite3PagerOpenWal()`/`sqlite3PagerCloseWal()`, optional `sqlite3PagerWalWriteLock()`/`sqlite3PagerWalDb()`, optional snapshot APIs, ZipVFS `sqlite3PagerWalFramesize()`, and SEH `sqlite3PagerWalSystemErrno()`.

## Control Flow

Commit phase two first guards against a stale pager error. A valid caller must be in `PAGER_WRITER_LOCKED`, `PAGER_WRITER_FINISHED`, or WAL `PAGER_WRITER_CACHEMOD`. If the transaction never modified the database, the connection is in exclusive locking mode, and the journal mode is `PERSIST`, the already-written zero-record journal header is harmless as a future hot journal, so the pager simply returns to `PAGER_READER`. All other commits call `pager_end_transaction()` with the `setSuper` flag and `bCommit=1`. That helper, defined earlier, releases savepoints, finalizes rollback journals by close/delete, truncate, zero-header, or close-memory behavior, cleans or clears writable cache state, ends WAL write transactions, truncates oversized database files after rollback-mode commit, invokes `SQLITE_FCNTL_COMMIT_PHASETWO`, downgrades locks when appropriate, clears `setSuper`, and leaves the pager in `PAGER_READER`.

Rollback branches on the current state and journal family. In WAL mode it rolls back to transaction start by calling `sqlite3PagerSavepoint(..., SAVEPOINT_ROLLBACK, -1)`, then closes the WAL write transaction through `pager_end_transaction(..., bCommit=0)`. In rollback mode, if no journal is open or the pager never moved beyond `PAGER_WRITER_LOCKED`, it only ends the transaction. The special non-memory `journal_mode=off` path after cache modification marks the pager `PAGER_ERROR` because there is no durable image from which to restore dirty cache entries. Otherwise rollback replays the main rollback journal through `pager_playback()`. Any rollback error is routed through `pager_error()` so later callers observe a sticky error instead of reading from an uncertain cache.

Savepoint creation is incremental. `sqlite3PagerOpenSavepoint()` calls the noinline allocator only when the requested count exceeds `nSavepoint` and journaling is active. Each new savepoint snapshots the current database size, current main-journal write offset or first-header offset, and current sub-journal record count. It allocates a `Bitvec` sized to the database image and, in WAL mode, asks the WAL layer to record its savepoint data.

`sqlite3PagerSavepoint()` computes the new number of active savepoints as either `iSavepoint` for release or `iSavepoint+1` for rollback. It destroys bitvecs for all savepoints above that boundary. On release, if the released savepoint allows truncation and the sub-journal is an in-memory journal, it truncates the sub-journal file to `(pageSize+4)*iSubRec` and rewinds `nSubRec`. On rollback, if WAL is active or a rollback journal is open, it calls `pagerPlaybackSavepoint()`. That helper resets `dbSize` to `nOrig` or `dbOrigSize`, replays main-journal records after the savepoint offset, replays later journal headers through the effective `journalOff`, then replays sub-journal records not already restored; in WAL it delegates WAL undo with `sqlite3WalSavepointUndo()`. ZipVFS builds add a defensive error-state transition if savepoint rollback is impossible under `journal_mode=off` after cache modification.

`sqlite3PagerMovepage()` is the highest-risk local control flow. It first journals temp-file pages so in-memory rollback can restore the old location. If the page is already dirty and savepoints require a copy, it sub-journals the current content before changing the page number. It remembers the source page number when `PGHDR_NEED_SYNC` is set and the move is not a commit-time move, because that original page cannot be written until the journal containing its old content is synced. It then clears the flag on the moving page, looks up any target page already in cache, rejects unexpected multiple references as corruption, transfers the target's `PGHDR_NEED_SYNC` flag to the moving page, and either drops the target page or moves it out of the way for temp databases. After moving the source page to the new page number and marking it dirty, the function reloads the original `needSyncPgno` if necessary, sets `PGHDR_NEED_SYNC` on that reloaded page, and marks it dirty. If reload fails, it clears the corresponding `pInJournal` bit for original database pages so a future write will journal the page again instead of relying on an unsynced journal record.

Journal-mode switching changes `pPager->journalMode` only after caller-side validation. Memory databases are clamped to `MEMORY` or `OFF`; temporary databases are asserted never to request WAL. When leaving `TRUNCATE` or `PERSIST` for a non-persistent non-WAL mode outside exclusive locking mode, the pager closes the open journal handle, takes or reuses a RESERVED lock, deletes the old journal as an optimization, and restores the original `PAGER_OPEN` or `PAGER_READER` state. Switching to `OFF` or `MEMORY` closes the rollback journal handle. `sqlite3PagerOkToChangeJournalMode()` protects this flow by rejecting mode changes after cache modifications or after journal writes.

WAL open/close flows bridge pager lock state and the WAL module. `sqlite3PagerWalSupported()` requires locking support and either exclusive mode or VFS shared-memory methods (`xShmMap`). Internal `pagerOpenWal()` optionally takes an exclusive database lock first so the WAL index can live in heap memory in exclusive mode, then calls `sqlite3WalOpen()` with the VFS, database file descriptor, WAL path, exclusive flag, and journal-size limit. Public `sqlite3PagerOpenWal()` closes any rollback journal, opens WAL if this is a real non-WAL pager, sets `journalMode=WAL`, and resets state to `PAGER_OPEN`; if WAL is already open or this is a temp pager, it reports no-op through `pbOpen`. `sqlite3PagerCloseWal()` ensures an existing WAL file is opened if needed, takes an EXCLUSIVE database lock, checkpoints and closes through `sqlite3WalClose()`, clears `pWal`, refreshes mmap limits, and releases back to SHARED only if closing failed outside exclusive mode.

Checkpoint and snapshot adapters mostly pass through. `sqlite3PagerCheckpoint()` has one important bootstrap path: if `journalMode` says WAL but `pWal` is still null because a zero-byte database has not run a transaction since `PRAGMA journal_mode=WAL`, it executes `PRAGMA table_list` to force transaction startup before checkpointing. Snapshot APIs return `SQLITE_ERROR` unless a WAL handle exists; snapshot checking and unlocking forward to WAL lock management.

## State And Persistence Behavior

- `Pager.eState` is the central state machine touched here. Successful commit/rollback finalization returns to `PAGER_READER`; unrecoverable rollback/cache uncertainty uses `PAGER_ERROR`; WAL open can reset to `PAGER_OPEN` after switching journal mode.
- `Pager.iDataVersion` increments at commit phase two, signaling content change to higher layers and cache invalidation logic.
- Rollback-journal persistence is finalized by `pager_end_transaction()` according to journal mode. DELETE removes the journal, TRUNCATE truncates it, PERSIST zeroes or truncates headers, MEMORY closes the in-memory journal, and WAL mode ends the WAL write transaction rather than finalizing a rollback journal.
- `Pager.setSuper` is consumed by commit/rollback finalization. It affects persistent-journal handling because journals containing super-journal pointers must not be finalized by just zeroing the first header.
- `Pager.errCode` becomes sticky through `pager_error()` when rollback/commit finalization fails. The explicit `journal_mode=off` rollback branch uses `SQLITE_ABORT` and `setGetterMethod()` to prevent normal page reads from an untrusted cache.
- Savepoint state lives in `Pager.aSavepoint[]`, `nSavepoint`, `nSubRec`, `sjfd`, `pInSavepoint` bitvecs, and WAL savepoint cookies. Release frees higher savepoint bitvecs and may truncate the in-memory sub-journal; rollback replays journals and also discards higher savepoints.
- `Pager.dbSize`, `dbOrigSize`, and `dbFileSize` are coordinated with rollback and commit. Savepoint rollback resets `dbSize`; commit finalization can truncate the physical database file if it is larger than the committed image.
- `PGHDR_DIRTY` and `PGHDR_NEED_SYNC` on `PgHdr` objects are persistence barriers. `sqlite3PagerMovepage()` and savepoint playback carefully preserve these flags so dirty pages are not written before their old content is safely synced to the journal.
- `Pager.journalMode`, `exclusiveMode`, `journalSizeLimit`, `zJournal`, `zWal`, `pWal`, `walSyncFlags`, and the underlying `sqlite3_file` handles describe persistent journaling behavior. This chunk mutates those fields during PRAGMA journal/locking mode changes and WAL open/close.
- Cache statistics in `aStat[]` are cumulative counters exposed to `sqlite3_db_status()`. `sqlite3PagerCacheStat()` adds the selected counter to the caller's total and optionally resets that one counter.
- Filename access preserves legacy behavior for in-memory databases: `sqlite3PagerFilename(..., nullIfMemDb=1)` returns a stable empty-string pointer, while shared-cache matching can request the actual internal filename with `nullIfMemDb=0`.
- `Pager.pBackup` is not owned by this chunk, but exposing its address lets `backup.c` maintain the active backup list while the pager notifies backups on page writes and restarts elsewhere in the file.

## Dependencies And Integration Points

- The btree layer calls commit, rollback, savepoint, page movement, data/extra accessors, filename accessors, and mode setters. The pager enforces lower-level invariants but relies on btree/VDBE logic to call these APIs in legal transaction states.
- `pager_end_transaction()`, `pager_playback()`, `pagerPlaybackSavepoint()`, `pager_error()`, `pagerLockDb()`, `pagerUnlockDb()`, `pager_unlock()`, `sqlite3PagerSharedLock()`, `pager_reset()`, `pagerFixMaplimit()`, `assertTruncateConstraint()`, and `subjournalPageIfRequired()` are internal dependencies defined earlier in `pager.c`.
- The pcache layer is used through `sqlite3PcacheRefCount()`, `sqlite3PcachePagecount()`, `sqlite3PcacheGetCachesize()`, `sqlite3PcacheMove()`, `sqlite3PcacheDrop()`, `sqlite3PcacheMakeDirty()`, `sqlite3PcacheTruncate()`, and cache reset/clean helpers invoked indirectly by transaction finalization.
- The VFS/OS layer is used for locking, unlocking, deleting journal files, checking WAL existence, truncating sub-journals, and exposing `sqlite3_file` handles. Correct behavior depends on VFS implementations honoring lock levels and shared-memory support.
- The WAL layer owns `Wal` internals. This chunk only forwards to `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalCheckpoint()`, `sqlite3WalCallback()`, `sqlite3WalSavepoint()`, `sqlite3WalSavepointUndo()`, `sqlite3WalEndWriteTransaction()`, snapshot APIs, optional write-lock APIs, and size-limit/db-handle propagation.
- PRAGMA and VDBE opcode paths integrate through journal-mode, locking-mode, checkpoint, and WAL-open/close APIs. `sqlite3PagerCheckpoint()` may run SQL (`PRAGMA table_list`) through the database handle to initialize WAL state for a rare zero-byte database case.
- Auto-vacuum and btree page relocation depend on `sqlite3PagerMovepage()` preserving page references and page metadata ownership. The caller remains responsible for updating btree metadata stored in the page-extra area.
- Backup integration uses `sqlite3PagerBackupPtr()` for ownership and earlier write/playback paths for updates. Any change to page movement or rollback semantics must preserve backup notifications for pages written to the database file.
- Compile-time feature switches shape the surface: `SQLITE_OMIT_DISKIO` excludes the whole region, `SQLITE_OMIT_AUTOVACUUM` removes `sqlite3PagerMovepage()`, `SQLITE_OMIT_WAL` removes WAL functions, `SQLITE_ENABLE_SNAPSHOT` adds snapshot APIs, `SQLITE_ENABLE_SETLK_TIMEOUT` adds WAL write-lock/db-handle helpers, `SQLITE_ENABLE_ZIPVFS` adds savepoint error handling and WAL frame sizing, and `SQLITE_USE_SEH` adds WAL system-error exposure.

## Risks And Edge Cases

- Commit phase two is the point of no return for rollback-journal transactions. A regression in journal deletion/truncation/zeroing can leave a stale journal that later appears hot or can remove rollback evidence too early.
- The persistent-journal exclusive-mode fast path is valid only when the transaction has not modified the database and the journal header records zero pages. Expanding this optimization would risk committing without finalizing a meaningful hot journal.
- Rollback with `journal_mode=off` cannot reconstruct modified cache pages. The explicit `PAGER_ERROR` transition protects readers; removing it would allow stale dirty cache contents to leak after an aborted write transaction.
- Savepoint release indexes are subtle: release computes `nNew=iSavepoint`, then uses `aSavepoint[nNew]` as the released savepoint descriptor before it is logically discarded. Changing allocation/free ordering can create use-after-free or wrong sub-journal truncation.
- `PagerSavepoint.pInSavepoint` allocation can fail after `aSavepoint` is reallocated and partially initialized. The code advances `nSavepoint` only after each successful bitvec creation; callers must still handle `SQLITE_NOMEM_BKPT` with partially opened savepoints.
- Savepoint rollback must coordinate main-journal playback, sub-journal playback, and WAL undo. Missing the `pDone` bitvec behavior can replay stale records over newer restored content.
- `sqlite3PagerMovepage()` assumes no external reference to the page currently at the destination. If corruption or caller misuse leaves multiple references, it returns `SQLITE_CORRUPT_BKPT`; if that guard is weakened, page-cache aliasing could corrupt btree structure.
- The `PGHDR_NEED_SYNC` transfer/reload path in page movement is critical for power-failure safety. Failing to reload and dirty the original page, or failing to clear the `pInJournal` bit on reload error, can permit a database write before the journal is durable.
- Journal-mode deletion of old persistent/truncate journals is intentionally best-effort but must take a RESERVED lock first when not already reserved. Deleting without the lock can race another connection using the journal.
- `sqlite3PagerLockingMode()` refuses changes while WAL uses heap memory unless already exclusive. This prevents switching out of a lock mode that the WAL-index representation depends on.
- `sqlite3PagerCheckpoint()`'s `PRAGMA table_list` bootstrap can run SQL from a utility API. It is rare but important for reentrancy, interruption, and attached-database behavior.
- WAL close requires an EXCLUSIVE lock and may leave it held on success. Callers switching back to rollback mode must account for the lock state and handle `SQLITE_BUSY` without assuming the WAL handle was closed.
- Snapshot APIs deliberately return generic `SQLITE_ERROR` when not in WAL mode. Higher layers should validate mode/state before exposing snapshot operations to users.
- Accessor functions expose raw pointers (`sqlite3_file *`, VFS pointer, page data, extra bytes). Callers must respect pager lifetime, page reference counts, and build-mode differences such as `SQLITE_OMIT_WAL`.

## Test Signals

- Commit tests should cover rollback journal modes DELETE, TRUNCATE, PERSIST, MEMORY, OFF, exclusive locking, persistent journals with and without super-journal names, and the no-modification fast path.
- Fault-injection tests should simulate IO errors during journal finalization, database truncation, unlock, WAL close, and commit phase-two file-control so `pager_error()` and returned error priority remain stable.
- Rollback tests should cover WAL rollback, rollback-journal playback, no-open-journal rollback, `PAGER_WRITER_LOCKED` no-op rollback, and `journal_mode=off` cache-modified abort behavior.
- Savepoint tests should exercise nested release and rollback, rollback to non-top savepoints, transaction-level `iSavepoint=-1` rollback, in-memory sub-journal truncation on release, OOM during bitvec allocation, and WAL savepoint undo.
- Auto-vacuum/incremental-vacuum tests should move dirty pages with active savepoints, move pages that carry `PGHDR_NEED_SYNC`, move onto cached target pages, and inject allocation/IO failures in the reload path after `needSyncPgno`.
- Corruption tests should cover the destination-page multiple-reference guard in `sqlite3PagerMovepage()` and ensure it reports corruption rather than silently moving aliased pages.
- PRAGMA journal-mode tests should verify memory database clamping to MEMORY/OFF, temp database rejection of WAL by higher layers, cleanup of old persistent/truncate journal files, and `sqlite3PagerOkToChangeJournalMode()` rejection after modification.
- Locking-mode tests should cover normal/exclusive transitions with rollback journals, WAL shared-memory mode, WAL heap-memory exclusive mode, and temp pagers.
- WAL tests should cover VFS support detection with and without `xShmMap`, no-lock pagers, WAL open from `PAGER_READER` and `PAGER_OPEN`, rollback-journal handle closure when entering WAL, WAL close with existing on-disk logs, checkpoint modes, and checkpoint bootstrap for a zero-byte database after `PRAGMA journal_mode=WAL`.
- Snapshot-enabled builds should test get/open/recover/check/unlock in WAL mode and error returns outside WAL mode, including unavailable snapshots and busy checkpointer locks.
- ZipVFS and SEH-specific builds should cover `sqlite3PagerWalFramesize()`, savepoint rollback under `journal_mode=off`, and WAL system errno propagation.
- Cache-stat and pager-stat tests should verify counter accumulation/reset, memory-use estimates, refcount reporting, and that accessors return stable filename/journal/VFS/file-handle values across memory, temp, rollback, and WAL databases.
