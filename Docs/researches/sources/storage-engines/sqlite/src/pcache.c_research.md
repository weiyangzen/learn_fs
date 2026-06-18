# sources/storage-engines/sqlite/src/pcache.c

## Purpose

`pcache.c` implements SQLite's upper page-cache layer. It wraps the pluggable `sqlite3_pcache_methods2` backend with pager-facing `PgHdr` objects, dirty-page tracking, reference counting, page-size/cache-size/spill configuration, cache stress behavior, and dirty-list sorting. It is the bridge between the pager, which needs transaction-aware page state, and the lower pcache backend, which manages memory and lookup by page number.

The file's central invariant is that clean pages match backing storage, while dirty pages have modified contents that must be written, journaled, or otherwise resolved before they can be discarded. Dirty pages are maintained in an LRU-style list and can be sorted by page number when the pager needs a stable writeback order.

## Important Types and Functions

`struct PCache` stores dirty-list heads (`pDirty`, `pDirtyTail`), the `pSynced` optimization pointer, total references `nRefSum`, size settings (`szCache`, `szSpill`, `szPage`, `szExtra`), purgeability, `eCreate`, the pager stress callback, callback context, and the lower `sqlite3_pcache *pCache`.

Debug helpers include `sqlite3PcachePageSanity()` and optional tracing/dump helpers. Dirty-list management is centralized in `pcacheManageDirtyList()` with operations remove, add, and move-to-front. `pcacheUnpin()` delegates unpinning clean unreferenced purgeable pages to the backend.

Initialization and lifecycle APIs include `sqlite3PcacheInitialize()`, `sqlite3PcacheShutdown()`, `sqlite3PcacheSize()`, `sqlite3PcacheOpen()`, `sqlite3PcacheSetPageSize()`, `sqlite3PcacheClose()`, `sqlite3PcacheClear()`, and `sqlite3PcacheTruncate()`.

Fetch and reference APIs include `sqlite3PcacheFetch()`, `sqlite3PcacheFetchStress()`, `sqlite3PcacheFetchFinish()`, `sqlite3PcacheRelease()`, `sqlite3PcacheRef()`, `sqlite3PcacheDrop()`, `sqlite3PcacheRefCount()`, and `sqlite3PcachePageRefcount()`. Dirty-state APIs include `sqlite3PcacheMakeDirty()`, `sqlite3PcacheMakeClean()`, `sqlite3PcacheCleanAll()`, `sqlite3PcacheClearWritable()`, `sqlite3PcacheClearSyncFlags()`, `sqlite3PcacheMove()`, and `sqlite3PcacheDirtyList()`.

Sizing APIs include `sqlite3PcachePagecount()`, `sqlite3PcacheSetCachesize()`, `sqlite3PcacheSetSpillsize()`, `sqlite3PcacheShrink()`, `sqlite3HeaderSizePcache()`, and `sqlite3PCachePercentDirty()`.

## Control Flow

Opening a cache zeroes `PCache`, initializes defaults, records the pager stress callback, sets `eCreate` to the expensive-allocation path, then calls `sqlite3PcacheSetPageSize()` to allocate the lower cache through `pcache2.xCreate()`. Fetch is split for performance: `sqlite3PcacheFetch()` asks the backend for a raw `sqlite3_pcache_page`; `sqlite3PcacheFetchFinish()` converts the raw page into an initialized `PgHdr`, increments the page reference, and initializes page header fields only on first use.

If a create fetch fails because clean pages cannot be cheaply recycled, pager code can call `sqlite3PcacheFetchStress()`. That routine looks for an unreferenced dirty page, preferring one without `PGHDR_NEED_SYNC`, invokes the pager's `xStress` callback to clean/spill it, and then retries backend fetch with a hard create flag.

Dirty state transitions run through `sqlite3PcacheMakeDirty()` and `sqlite3PcacheMakeClean()`. Releasing a dirty page with refcount zero moves it to the front of the dirty list, while releasing a clean page unpins it in the backend. `sqlite3PcacheMove()` handles page-number changes by dropping any existing destination page, rekeying the backend, updating `PgHdr.pgno`, and moving NEED_SYNC dirty pages forward in the dirty list.

## State and Persistence Behavior

`PgHdr.flags` encode clean/dirty, writable, need-sync, don't-write, mmap, and WAL append state. `pcache.c` does not write disk content itself; persistence is enforced by preserving enough state for pager code to journal, sync, spill, and write in a safe order. The `PGHDR_NEED_SYNC` flag is deliberately independent of `PGHDR_WRITEABLE`, because pages may temporarily stop being writable and later become writable again while still requiring a journal sync before database writeback.

`pSynced` is an optimization for finding dirty pages safe to spill without forcing a journal sync. It may be approximate; correctness comes from checking flags while scanning. `eCreate` tracks whether the lower cache may allocate only cheaply or may try harder, based on whether the cache is purgeable and has dirty pages. Truncation cleans and discards pages above a page number, with a special case that preserves and zeroes page 1 if it is still referenced during full reset.

## Dependencies and Integration Points

This layer depends on `sqlite3GlobalConfig.pcache2`, `sqliteInt.h`, `pcache.h`, `PgHdr`, `Pager`, and pager-provided stress callbacks. Pager code relies on dirty-list output sorted by page number for commit/writeback work. The lower default backend is `pcache1.c`, but this layer also supports application-provided pcache implementations through `SQLITE_CONFIG_PCACHE2`.

## Risks and Edge Cases

Dirty-list corruption is the main local risk; `pDirtyNext`, `pDirtyPrev`, `pDirty`, `pDirtyTail`, and `pSynced` must remain consistent across dirty, clean, release, drop, move, and truncate operations. Reference counts must be balanced across fetch, finish, ref, release, and drop. `sqlite3PcacheSetPageSize()` requires no outstanding refs and no dirty pages. `sqlite3PcacheFetchStress()` must tolerate `SQLITE_BUSY` from the stress callback and must not recycle referenced pages. `sqlite3PcacheDirtyList()` repurposes `PgHdr.pDirty` as a singly linked sorted chain, so callers must not expect `pDirtyPrev` to remain meaningful in that returned list.

## Test Signals

Tests should check fetch/fetch-finish initialization, balanced refcounts, clean-page unpinning, dirty-page list membership, sorted dirty list order, moving pages over existing cached pages, truncating with page 1 referenced, cache-size and negative KiB cache-size behavior, spill threshold behavior, stress callback error and busy handling, debug page sanity assertions, `SQLITE_CHECK_PAGES` dirty iteration, and dirty percentage calculations.
