# sources/storage-engines/sqlite/src/pcache.h

## Purpose

`pcache.h` declares the pager-facing page-cache API and the public portion of `PgHdr`. It is the contract between pager code, btree page extras, and the pcache implementation in `pcache.c` plus the pluggable backend. The header defines how cached database pages expose page data, extra per-page storage, pager ownership, dirty linkage, page number, flags, and reference operations.

## Important APIs, Types, and Constants

The main types are `PgHdr` and `PCache`. `PgHdr` begins with fields visible to other modules: `sqlite3_pcache_page *pPage`, `pData`, `pExtra`, owning `PCache *pCache`, transient sorted-list pointer `pDirty`, owning `Pager *pPager`, optional `pageHash`, `pgno`, and `flags`. The later fields are private to `pcache.c`: `nRef`, `pDirtyNext`, and `pDirtyPrev`.

Flag bits define page state: `PGHDR_CLEAN`, `PGHDR_DIRTY`, `PGHDR_WRITEABLE`, `PGHDR_NEED_SYNC`, `PGHDR_DONT_WRITE`, `PGHDR_MMAP`, and `PGHDR_WAL_APPEND`. These flags are interpreted by pager and pcache code to decide whether pages can be modified, skipped, spilled, synced, or treated as mmap/WAL-specific pages.

Lifecycle APIs are `sqlite3PcacheInitialize()`, `sqlite3PcacheShutdown()`, `sqlite3PCacheBufferSetup()`, `sqlite3PcacheOpen()`, `sqlite3PcacheSetPageSize()`, `sqlite3PcacheSize()`, `sqlite3PcacheClose()`, `sqlite3PcacheClear()`, and `sqlite3PCacheSetDefault()`.

Fetch/reference APIs are `sqlite3PcacheFetch()`, `sqlite3PcacheFetchStress()`, `sqlite3PcacheFetchFinish()`, `sqlite3PcacheRelease()`, `sqlite3PcacheRef()`, `sqlite3PcacheRefCount()`, and `sqlite3PcachePageRefcount()`. Mutation and state APIs include `sqlite3PcacheDrop()`, `sqlite3PcacheMakeDirty()`, `sqlite3PcacheMakeClean()`, `sqlite3PcacheCleanAll()`, `sqlite3PcacheClearWritable()`, `sqlite3PcacheMove()`, `sqlite3PcacheTruncate()`, `sqlite3PcacheDirtyList()`, `sqlite3PcacheClearSyncFlags()`, and `sqlite3PcacheShrink()`.

Sizing and diagnostics include `sqlite3PcacheSetCachesize()`, optional `sqlite3PcacheGetCachesize()`, `sqlite3PcacheSetSpillsize()`, optional `sqlite3PcacheReleaseMemory()`, optional `sqlite3PcacheStats()`, `sqlite3HeaderSizePcache()`, `sqlite3HeaderSizePcache1()`, `sqlite3PCachePercentDirty()`, optional `sqlite3PCacheIsDirty()`, optional `sqlite3PcacheIterateDirty()`, and debug-only `sqlite3PcachePageSanity()`.

## Control Flow

Callers initialize the subsystem, allocate storage for a `PCache` using `sqlite3PcacheSize()`, open it with page and extra sizes, fetch raw pages, finish them into `PgHdr` objects, and release each successful fetch. Pages become dirty through `sqlite3PcacheMakeDirty()` after pager write authorization. Clean transitions happen after pager writeback or rollback. Truncation, move, and dirty-list retrieval support vacuum, rollback, commit, and database-size changes.

The fetch split is part of the interface: `sqlite3PcacheFetch()` returns a backend page object, and `sqlite3PcacheFetchFinish()` makes it safe to use as `PgHdr`. `sqlite3PcacheFetchStress()` is a second-stage allocation path used after a normal fetch cannot cheaply create a page.

## State and Persistence Behavior

`pcache.h` exposes state that determines persistence safety but delegates actual disk work to pager. `PGHDR_WRITEABLE` means the page has been journaled and may be modified. `PGHDR_NEED_SYNC` means the rollback journal must be synced before the page is written to the database. `PGHDR_DONT_WRITE` marks a dirty page whose content should not be written back. `PGHDR_WAL_APPEND` marks pages appended to WAL. Reference counts pin pages in memory; unreferenced clean pages can be recycled, while unreferenced dirty pages remain available for pager-managed spill.

## Dependencies and Integration Points

This header depends on `Pager`, `Pgno`, `sqlite3_pcache_page`, and SQLite configuration macros. It is included by pager and pcache implementation code, and it exposes header-size queries so SQLite can compute the full per-page memory layout used by btree, pcache, and pcache1. `sqlite3PCacheBufferSetup()` integrates with `sqlite3_config(SQLITE_CONFIG_PAGECACHE)`. `sqlite3PCacheSetDefault()` installs the default backend when no application backend is configured.

## Risks and Edge Cases

Consumers must respect which `PgHdr` fields are public and which are private. Incorrect flag manipulation can violate journaling invariants. Every successful fetch needs a release. `sqlite3PcacheSetPageSize()` requires no live page references. `sqlite3PcacheDirtyList()` returns a sorted list using `PgHdr.pDirty`, not the same links as the internal dirty LRU list. Optional compile flags change available diagnostics and direct-overflow behavior.

## Test Signals

Tests should cover flag transitions, dirty-list membership, page fetch/release reference accounting, cache close with no outstanding refs, configured pagecache buffer setup, spill-size and cache-size setting, memory-release builds, dirty iteration under `SQLITE_CHECK_PAGES`, debug sanity checks, and direct-overflow dirty detection when enabled.
