# sources/storage-engines/sqlite/src/pager.h

## Purpose

`pager.h` is the public internal interface for SQLite's pager subsystem. The pager sits between btree/database logic and the VFS/page-cache layers. It reads and writes database files one page at a time, manages rollback journal or WAL modes, owns transactional state transitions, exposes page reference operations, and provides configuration hooks for cache size, page size, synchronous behavior, locking, mmap, savepoints, and checkpointing.

This header does not define the `Pager` structure itself. It declares the opaque `Pager` handle and the `DbPage` alias for `PgHdr`, so callers can manipulate pages without depending on pager internals. Its constants intentionally mirror API-visible behavior such as `PRAGMA journal_mode` values and btree open flags.

## Important APIs, Types, and Constants

The core types are `Pgno`, `Pager`, and `DbPage`. `Pgno` is a 32-bit page number with page 1 as the first valid database page and 0 reserved for "not a page". `Pager` is an opaque per-open-file manager. `DbPage` is a page handle backed by `PgHdr` from the pcache layer.

Open and close are handled by `sqlite3PagerOpen()`, `sqlite3PagerClose()`, and `sqlite3PagerReadFileheader()`. Pager configuration includes `sqlite3PagerSetPagesize()`, `sqlite3PagerMaxPageCount()`, `sqlite3PagerSetCachesize()`, `sqlite3PagerSetSpillsize()`, `sqlite3PagerSetMmapLimit()`, `sqlite3PagerSetFlags()`, `sqlite3PagerLockingMode()`, `sqlite3PagerSetJournalMode()`, `sqlite3PagerJournalSizeLimit()`, and `sqlite3PagerFlush()`.

Page access is through `sqlite3PagerGet()`, `sqlite3PagerLookup()`, `sqlite3PagerRef()`, `sqlite3PagerUnref()`, `sqlite3PagerUnrefNotNull()`, and `sqlite3PagerUnrefPageOne()`. Mutating a page requires `sqlite3PagerWrite()`, after which `sqlite3PagerDontWrite()` and `sqlite3PagerMovepage()` can adjust persistence behavior or page identity. `sqlite3PagerGetData()` and `sqlite3PagerGetExtra()` bridge from pager pages to page data and btree-owned extra storage.

Transaction and durability APIs include `sqlite3PagerBegin()`, `sqlite3PagerCommitPhaseOne()`, `sqlite3PagerSync()`, `sqlite3PagerCommitPhaseTwo()`, `sqlite3PagerRollback()`, `sqlite3PagerOpenSavepoint()`, `sqlite3PagerSavepoint()`, `sqlite3PagerSharedLock()`, and `sqlite3PagerExclusiveLock()`. WAL builds add `sqlite3PagerCheckpoint()`, `sqlite3PagerWalSupported()`, `sqlite3PagerWalCallback()`, `sqlite3PagerOpenWal()`, `sqlite3PagerCloseWal()`, and optional snapshot functions.

Key constants include `PAGER_OMIT_JOURNAL`, `PAGER_MEMORY`, `PAGER_LOCKINGMODE_*`, `PAGER_JOURNALMODE_*`, `PAGER_GET_NOCONTENT`, `PAGER_GET_READONLY`, and `PAGER_SYNCHRONOUS_*`. `PAGER_SJ_PGNO()` identifies the special journal page number used to mark a super-journal name payload.

## Control Flow and State

Typical control flow starts with `sqlite3PagerOpen()`, then configuration, then shared locking and page fetches. Read-only paths fetch pages with `sqlite3PagerGet()` or `sqlite3PagerLookup()`, increment or release references, and inspect page data. Write paths call `sqlite3PagerBegin()`, fetch a page, call `sqlite3PagerWrite()` to journal and mark it writable, update the page buffer, then commit through phase one, sync, and phase two, or roll back through `sqlite3PagerRollback()`.

The pager state machine is represented behind the opaque `Pager` type, but the API reveals its key transitions: lock acquisition, page-cache population, journal-mode selection, savepoint creation and rollback, write preparation, sync, commit finalization, and cache truncation. The `PAGER_GET_*` flags allow callers to avoid disk reads when the caller will overwrite page content or to accept a read-only page.

## Persistence Behavior

Persistence is controlled by journal mode, synchronous flags, locking mode, and savepoint state. Rollback journal modes include delete, persist, truncate, memory, and off; WAL mode is exposed when WAL is compiled in. Synchronous values map to `PRAGMA synchronous`, and additional bits map to fullfsync, checkpoint fullfsync, and cache spill. `sqlite3PagerDontWrite()` allows a page to remain dirty in memory while avoiding a database-file write in cases where pager invariants make the write unnecessary. `sqlite3PagerTruncateImage()` changes the pager's view of database size before the database file is physically truncated.

## Dependencies and Integration Points

`pager.h` depends on SQLite core types from `sqliteInt.h`, VFS handles (`sqlite3_vfs`, `sqlite3_file`), btree-compatible flags, the pcache `PgHdr` type, backup handles, WAL support, and optional snapshot/SEH/ZIPVFS features. Btree code uses this API for page-level transactional access. PRAGMA code configures pager modes and durability using these declarations. WAL and checkpoint subsystems use the WAL-specific functions. Test builds use `sqlite3PagerStats()`, `sqlite3PagerRefdump()`, and simulated I/O error toggles.

## Risks and Edge Cases

The numeric journal-mode values are API-visible and cannot be renumbered without compatibility breakage. `PAGER_OMIT_JOURNAL` and `PAGER_MEMORY` must match btree flags. Misuse of `sqlite3PagerWrite()` can corrupt persistence semantics because page buffers must be journaled before modification. Locking mode and WAL transitions require careful sequencing, and `sqlite3PagerOkToChangeJournalMode()` exists to guard unsafe changes. `PAGER_SJ_PGNO` depends on page size and the pending-byte location, so page-size changes interact with journal interpretation.

## Test Signals

Useful tests include transaction commit and rollback across all rollback journal modes, WAL open/close/checkpoint behavior, savepoint rollback of dirty pages, page-size changes with no outstanding references, mmap/direct-overflow reads, `PRAGMA synchronous` and `journal_mode` conformance, simulated I/O errors, power-loss style journal sync tests, lock timeout behavior when enabled, and reference-count sanity checks under debug builds.
