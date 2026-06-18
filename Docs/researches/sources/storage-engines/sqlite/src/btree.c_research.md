# Research: sources/storage-engines/sqlite/src/btree.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008765`: lines 1-7568, `Docs/researches/chunks/subset-b-008765_research.md`
- `subset-b-008766`: lines 7569-11600, `Docs/researches/chunks/subset-b-008766_research.md`

## Chunk Research

### subset-b-008765: lines 1-7568

# sources/storage-engines/sqlite/src/btree.c lines 1-7568

## Scope And Purpose

This chunk is the opening and majority of SQLite's disk-backed b-tree implementation. It starts with file-level setup and shared-cache support, then covers cursor state management, page parsing and local page-space management, database open/close and pager configuration, transaction and savepoint control, auto-vacuum pointer-map maintenance, cursor creation and navigation, payload access through local and overflow storage, page allocation/free-list management, overflow cleanup, and the cell construction/insertion helpers used by later balancing and mutation code.

The source implements the b-tree layer that sits between SQL/VDBE table or index operations and the pager. It translates logical table/index root pages, rowid keys, index keys, and payloads into the SQLite file format: database page 1 header fields, b-tree page headers, cell pointer arrays, local payload fragments, overflow chains, free-list trunk/leaf pages, pointer-map pages for auto-vacuum, and pager transactions. This chunk stops immediately after defining the balancing constants `NN` and `NB` and introducing the `CellArray` comment block; the concrete page-rebalancing implementation continues in the next chunk.

## Important APIs, Types, And Flags

The primary public entry points in this chunk are the `sqlite3Btree*` APIs consumed by higher SQLite layers:

- Connection and configuration: `sqlite3BtreeOpen`, `sqlite3BtreeClose`, `sqlite3BtreeSetCacheSize`, `sqlite3BtreeSetSpillSize`, `sqlite3BtreeSetMmapLimit`, `sqlite3BtreeSetPagerFlags`, `sqlite3BtreeSetPageSize`, `sqlite3BtreeGetPageSize`, `sqlite3BtreeGetReserveNoMutex`, `sqlite3BtreeGetRequestedReserve`, `sqlite3BtreeMaxPageCount`, `sqlite3BtreeSecureDelete`, `sqlite3BtreeSetAutoVacuum`, `sqlite3BtreeGetAutoVacuum`, and `sqlite3BtreeNewDb`.
- Transaction control: `sqlite3BtreeBeginTrans`, `sqlite3BtreeCommitPhaseOne`, `sqlite3BtreeCommitPhaseTwo`, `sqlite3BtreeCommit`, `sqlite3BtreeRollback`, `sqlite3BtreeBeginStmt`, `sqlite3BtreeSavepoint`, and `sqlite3BtreeIncrVacuum`.
- Cursor lifecycle and positioning: `sqlite3BtreeCursor`, `sqlite3BtreeCursorSize`, `sqlite3BtreeCursorZero`, `sqlite3BtreeCloseCursor`, `sqlite3BtreeClearCursor`, `sqlite3BtreeCursorHasMoved`, `sqlite3BtreeCursorRestore`, `sqlite3BtreeCursorHint`, `sqlite3BtreeCursorHintFlags`, `sqlite3BtreeFirst`, `sqlite3BtreeLast`, `sqlite3BtreeTableMoveto`, `sqlite3BtreeIndexMoveto`, `sqlite3BtreeNext`, `sqlite3BtreePrevious`, `sqlite3BtreeEof`, and `sqlite3BtreeIsEmpty`.
- Cursor data access: `sqlite3BtreeIntegerKey`, `sqlite3BtreePayloadSize`, `sqlite3BtreePayload`, `sqlite3BtreePayloadChecked`, `sqlite3BtreePayloadFetch`, `sqlite3BtreeOffset`, `sqlite3BtreeMaxRecordSize`, `sqlite3BtreeRowCountEst`, `sqlite3BtreeCursorPin`, and `sqlite3BtreeCursorUnpin`.
- Shared-cache and conflict handling: `sqlite3_enable_shared_cache`, `sqlite3BtreeTripAllCursors`, and internal helpers that enforce per-table read/write locks.

Key structures are defined in `btreeInt.h` but are heavily manipulated here:

- `Btree` is the per-connection handle. It tracks the owning `sqlite3 *db`, transaction state, shared-cache links, table lock record for schema root, and whether the handle is sharable.
- `BtShared` is the shared b-tree state behind one pager/database file. It owns the pager, mutex, page-size and usable-size configuration, page-1 reference, schema pointer, cursor list, lock list, free temp space for cell construction, transaction counters, auto-vacuum flags, secure-delete flags, `pHasContent` bitvec, and page-count state.
- `MemPage` wraps a pager page and caches decoded b-tree page metadata: page number, header offset, page type flags, cell count, free byte count, cell pointer array, max/min local payload thresholds, and type-specific function pointers `xParseCell` and `xCellSize`.
- `BtCursor` tracks a traversal path through a table or index b-tree. It stores the current page, parent page stack, cell indices, root page, key-info for indexes, cursor flags, saved key for deferred restoration, overflow-page cache, and current `CellInfo`.
- `CellInfo` is the parsed representation of one cell: logical key, payload size, local payload size, cell byte size, and pointer to local payload.
- `BtreePayload` is used by `fillInCell` to assemble a new table or index cell from key/data/zero-fill inputs.

Important compile-time and runtime flags include:

- `BTALLOC_ANY`, `BTALLOC_EXACT`, and `BTALLOC_LE` control `allocateBtreePage` free-list selection.
- `PTF_*` page type flags are decoded into table-vs-index, leaf-vs-internal, intkey, and payload behavior.
- `BTCF_*` cursor flags record write cursors, multiple cursors on one root, valid cached key/payload metadata, valid overflow-cache state, pinned cursors, and last-entry positioning.
- `BTS_*` shared btree flags track read-only status, fixed page size, secure delete/overwrite behavior, exclusive/pending shared-cache writer state, initially-empty state, WAL restrictions, and auto-vacuum truncation work.
- `PTRMAP_*` pointer-map entry types describe child b-tree pages, root pages, free pages, first overflow pages, and subsequent overflow pages.

## Shared Cache And Locking

Shared-cache support is built around a global `sqlite3SharedCacheList` of `BtShared` objects protected by `SQLITE_MUTEX_STATIC_MAIN`. `sqlite3_enable_shared_cache` flips the global default for future opens. If SQLite is compiled without shared-cache support, the table-lock routines are compiled into no-ops and single-user assumptions apply.

When shared cache is enabled, `querySharedCacheTableLock` checks whether a `Btree` handle can take a read or write lock on a table root page. It rejects conflicting table locks from other `Btree` handles and records blocking relationships through `sqlite3ConnectionBlocked`. It also handles exclusive writer state through `BTS_EXCLUSIVE` and pending writer state through `BTS_PENDING`.

`setSharedCacheTableLock` installs or upgrades a `BtLock` entry for a handle/table pair after conflict checking succeeds. `clearAllSharedCacheTableLocks` removes locks held by a handle at transaction end, clears writer/exclusive/pending state where appropriate, and frees heap-allocated non-schema locks. `downgradeAllSharedCacheTableLocks` converts a writer's table locks to read locks when a connection still has active readers and the write transaction is being downgraded.

Debug-only helpers `hasSharedCacheTableLock` and `hasReadConflicts` enforce assumptions around cursor opens and writes. They account for schema-table write locks, index roots mapping back to owning table roots, read-uncommitted readers, and imposter-style duplicate root-page cases where exact validation is intentionally relaxed.

## Cursor State And Restoration

The cursor code protects higher layers from structural b-tree changes by saving logical positions before pages are modified. `saveCursorKey` stores either an integer rowid for table btrees or an allocated copy of the index key payload with padding for defensive record unpacking. `saveCursorPosition` releases page references, marks the cursor `CURSOR_REQUIRESEEK`, and clears cached payload/overflow/last-entry flags. It refuses to move pinned cursors with `SQLITE_CONSTRAINT_PINNED`.

`saveAllCursors` scans the shared cursor list for cursors on a root page and defers to `saveCursorsOnList` only when needed. This is important because the common case is one cursor or no affected cursor. `sqlite3BtreeTripAllCursors` is stronger: it marks cursors `CURSOR_FAULT` after rollback or serious invalidation, optionally preserving read-only cursors by saving their positions when only write cursors need to be tripped.

`btreeRestoreCursorPosition` re-seeks using the saved key and frees saved key memory on success. `sqlite3BtreeCursorHasMoved` exploits `BtCursor.eState` at struct offset zero for a fast validity check, while `sqlite3BtreeCursorRestore` restores and reports whether the exact original row survived.

Overflow caches are cursor-local and invalidated aggressively. `invalidateOverflowCache` clears one cursor's cache flag, `invalidateAllOverflowCache` clears every cursor on a shared btree, and `invalidateIncrblobCursors` invalidates incremental-blob cursors whose row or table is being modified.

## Page Format Parsing And Page-Space Management

This chunk contains the core low-level page and cell decoding logic. `get2byteNotZero` handles the file-format convention where a 2-byte zero cell-content offset means 65536 on a 64 KiB page. `decodeFlags` validates the page type byte and assigns the correct `MemPage` function pointers:

- table internal pages use `btreeParseCellPtrNoPayload` and `cellSizePtrNoPayload`;
- table leaf pages use `btreeParseCellPtr` and `cellSizePtrTableLeaf`;
- index internal pages use `btreeParseCellPtrIndex` and `cellSizePtr`;
- index leaf pages use `btreeParseCellPtrIndex` and `cellSizePtrIdxLeaf`.

`btreeParseCellAdjustSizeForOverflow` and `btreePayloadToLocal` implement the SQLite file-format rule for local-vs-overflow payload split. The calculation intentionally minimizes wasted overflow-page space while keeping local payload between page-type-specific min/max thresholds; changing this logic would change the file format.

`btreeInitPage` decodes a pager page into `MemPage` metadata. It validates page type, cell count, header offsets, local payload thresholds, and, when `PRAGMA cell_size_check` is enabled, calls `btreeCellSizeCheck` to verify cell offsets and sizes. `zeroPage` initializes a writable empty b-tree page with the requested flags.

In-page free space is managed by `btreeComputeFreeSpace`, `pageFindSlot`, `allocateSpace`, `freeSpace`, and `defragmentPage`. These routines maintain the b-tree page freeblock chain, cell content area, cell pointer array, and fragment byte count. They include many corruption checks for out-of-order freeblocks, offsets outside usable space, overlapping freeblocks, invalid fragment accounting, and impossible cell offsets.

`defragmentPage` has a fast path for pages with at most a couple of freeblocks and bounded fragmentation, otherwise it reconstructs the cell content region from a pager temp buffer. `freeSpace` coalesces adjacent freeblocks and honors secure-delete modes by zeroing returned bytes when `BTS_FAST_SECURE` is set.

## Pager And Database Open/Close Flow

`sqlite3BtreeOpen` is the main constructor. It classifies memory/temp/file databases, applies `BTREE_MEMORY`, handles `SQLITE_OPEN_MAIN_DB` vs temporary opens, allocates a `Btree`, and either attaches to an existing shared `BtShared` or creates a new pager through `sqlite3PagerOpen`. For shared cache, it canonicalizes the filename through the VFS, searches `sqlite3SharedCacheList`, rejects duplicate opens of the same `BtShared` inside one database connection, and links sharable `Btree` handles in address order for deadlock-safe mutex acquisition.

When a new `BtShared` is created, the code reads the first 100 bytes of the database header, initializes page-size and reserve-byte state, detects read-only pager state, applies compile-time secure-delete defaults, sets mmap limits, installs the pager busy-handler callback, and sets pager cache defaults after open succeeds.

`lockBtree` obtains a shared pager lock, loads page 1, validates the SQLite header and file-format bytes, handles WAL read/write versions, adjusts page size if the file header differs from the current setting, validates usable size, initializes auto-vacuum flags from page-1 metadata, computes payload thresholds, and records `pBt->pPage1` and `pBt->nPage`. Empty files can later be initialized by `newDatabase`, which writes the database header, page-size/reserve fields, payload fractions, auto-vacuum metadata, and an empty table b-tree root on page 1.

`sqlite3BtreeClose` rolls back any open transaction, removes shared-cache references, closes the pager when the last `BtShared` reference disappears, frees schema and temp-space allocations, unlinks shared-cache sibling pointers, and frees the `Btree` handle. Page references are carefully handled through `releasePage`, `releasePageOne`, and `releasePageNotNull`; page 1 uses a specialized pager unref path.

## Transactions, Savepoints, And Commit/Rollback

`sqlite3BtreeBeginTrans` is the public transaction entry. The fast path avoids the heavier helper if the handle already has a sufficient non-shared transaction. The full `btreeBeginTrans` path enters the btree mutex, rejects writes to read-only databases, enforces shared-cache writer conflicts, takes a schema read lock, invokes `lockBtree` until page 1 is ready, starts pager write transactions when requested, initializes new empty databases, updates page-1 database-size metadata if needed, records schema version for callers, and opens pager savepoint state matching the connection's SQL savepoint depth.

The busy-handler behavior is deliberate: if a write upgrade would deadlock with another reader/writer combination, the code returns busy/locked without invoking the busy callback in cases where waiting would not make progress.

Commit is split into two phases. `sqlite3BtreeCommitPhaseOne` optionally runs full auto-vacuum work, truncates the pager image if auto-vacuum moved pages, and calls `sqlite3PagerCommitPhaseOne`. `sqlite3BtreeCommitPhaseTwo` finalizes the pager commit, adjusts the data-version compensation, clears `pHasContent`, and ends/downgrades/clears btree transaction state through `btreeEndTransaction`. `sqlite3BtreeCommit` runs both phases for the normal single-file case.

Rollback first saves or trips cursors depending on `tripCode`, calls `sqlite3PagerRollback` for write transactions, reloads page count from page 1, clears write transaction state and `pHasContent`, and delegates final lock cleanup to `btreeEndTransaction`. `sqlite3BtreeSavepoint` rolls back or releases pager savepoints, rebuilds an empty database if a rollback returns to an initially empty state, and refreshes page count. `sqlite3BtreeBeginStmt` opens an anonymous pager savepoint for statement-level rollback.

## Auto-Vacuum And Pointer Maps

When auto-vacuum is enabled, pointer-map pages record who owns each movable page. `ptrmapPageno`, `ptrmapPut`, and `ptrmapGet` calculate pointer-map locations and read/write 5-byte entries. `ptrmapPut` refuses page zero, detects impossible use of a pointer-map page as a b-tree page, and writes entries through the pager only when content changes.

`setChildPtrmaps` updates pointer-map entries for all child b-tree pages and cell overflow pages reachable from a b-tree page. `modifyPagePointer` rewrites the actual parent/overflow pointer that refers to a moved page. `relocatePage` moves a page with `sqlite3PagerMovepage`, updates child pointer maps if the moved page is a b-tree page, updates next-overflow pointer maps if it is an overflow page, then rewrites the parent page's pointer and updates the moved page's pointer-map entry.

`incrVacuumStep` performs one unit of incremental-vacuum work by ensuring the current last page is free or moving it into a free page below the final target size. `finalDbSize` computes the target size after accounting for free pages, pointer-map pages, and the pending-byte page. `sqlite3BtreeIncrVacuum` wraps one incremental step inside a write transaction, saving cursors and invalidating overflow caches. `autoVacuumCommit` performs the full auto-vacuum sequence before commit, optionally consulting `db->xAutovacPages` to limit the number of pages vacuumed, then updates page-1 free-list and database-size fields and schedules pager truncation.

## Cursor Creation, Search, And Traversal

`btreeCursor` validates transaction state, table locks, write permissions, and read-conflict assumptions, then links a cursor into `BtShared.pCursor`. It marks all cursors on the same root with `BTCF_Multiple`, initializes write-cursor temp space on the first writer, and sets pager get flags for read-only cursors. `sqlite3BtreeCursor` wraps this with locking only when the btree is sharable.

`moveToRoot`, `moveToChild`, `moveToParent`, `moveToLeftmost`, and `moveToRightmost` maintain the cursor page stack. `moveToRoot` handles an empty btree, validates that the root page type matches table-vs-index expectations, and supports the page-1 virtual-root case where page 1 has no cells and one child. Child traversal validates depth limits, child page type consistency, and non-empty child pages.

`sqlite3BtreeFirst`, `sqlite3BtreeLast`, and `sqlite3BtreeIsEmpty` are thin cursor-positioning APIs. `sqlite3BtreeNext` and `sqlite3BtreePrevious` provide optimized fast paths for leaf-page neighbor movement and call `btreeNext`/`btreePrevious` for restoration, page-stack transitions, and internal-page traversal. They clear cached cell and overflow metadata before movement.

`sqlite3BtreeTableMoveto` searches intkey table btrees by rowid. It includes optimizations for repeated access to the current key, append-like `next rowid` movement, and right-biased search. It descends by binary search within each page and returns comparison status in `*pRes`.

`sqlite3BtreeIndexMoveto` searches index btrees using an `UnpackedRecord` and a comparison routine from `sqlite3VdbeFindCompare`. It includes last-page optimizations, compares small local index records directly out of the page, and falls back to full cell parsing plus `accessPayload` when a key spans overflow pages. Corrupt or suspicious key sizes are rejected before allocation.

## Payload And Overflow Handling

`getCellInfo` lazily fills `BtCursor.info` with parsed cell metadata. `sqlite3BtreeIntegerKey`, `sqlite3BtreePayloadSize`, `sqlite3BtreePayloadFetch`, `sqlite3BtreeOffset`, and `sqlite3BtreeMaxRecordSize` expose the current cell's key, payload metadata, direct local payload pointer, file offset, and a conservative maximum record-size bound.

`accessPayload` is the central payload reader/writer. It copies the local portion from the b-tree page and then walks the overflow chain for remaining bytes. It lazily allocates and populates `BtCursor.aOverflow`, uses pointer-map hints in auto-vacuum mode through `getOverflowPage`, validates overflow page numbers, and supports direct file reads under `SQLITE_DIRECT_OVERFLOW_READ` when no dirty page-cache state requires normal pager access. Writes call `sqlite3PagerWrite` before modifying any page or overflow page.

`sqlite3BtreePayload` assumes a valid cursor and delegates directly to `accessPayload`. `sqlite3BtreePayloadChecked`, used by incremental blob reads, can restore a moved cursor first and returns `SQLITE_ABORT` if the cursor is invalid.

`clearCellOverflow` frees all overflow pages associated with a cell. It validates that the cell's overflow pointer lies inside the page, checks each overflow page number, detects unexpected extra page references before freeing, and frees pages through `freePage2`. The `BTREE_CLEAR_CELL` macro combines cell parsing with overflow cleanup for later delete/update paths.

## Page Allocation, Freeing, And Cell Construction

`allocateBtreePage` obtains a writable unused page either from the free-list or by extending the database image. It updates page-1 free-list count and database-size fields through pager writes, supports exact and less-than-or-equal allocation modes for auto-vacuum relocation, searches free-list trunk/leaf entries as needed, skips pending-byte and pointer-map pages, and uses `PAGER_GET_NOCONTENT` only when rollback safety permits. It validates free-list trunk page numbers, leaf counts, and allocated page ranges.

`freePage2` adds a page to the free-list. It increments the free-page count, optionally zeroes page content for secure delete, records `PTRMAP_FREEPAGE` in auto-vacuum mode, and either appends the page as a free-list leaf to the current trunk or makes it the new trunk. The code intentionally preserves the historical limit that avoids using the last six trunk entries for backward compatibility with older SQLite versions. `btreeSetHasContent`, `btreeGetHasContent`, and `btreeClearHasContent` preserve rollback correctness when a page is freed and then reused within one transaction under no-content pager optimizations.

`fillInCell` formats a table or index cell into caller-provided storage. It writes the varint header, copies payload from key/data buffers, zero-fills requested tail bytes, computes the local payload split, allocates overflow pages when needed, writes overflow-chain pointers, and updates pointer-map entries for overflow pages in auto-vacuum databases. Debug builds reparse the partially constructed cell to verify computed header and local-size values.

`dropCell` removes a cell pointer and returns its local cell bytes to the page free-list without freeing overflow pages. `insertCell` and `insertCellFast` insert a cell pointer and local cell bytes into a page if space exists, or register the cell in `MemPage.apOvfl`/`aiOvfl` for later balancing if it does not. `insertCell` also supports overriding the first 4 bytes with a child page number for internal-page divider cells; `insertCellFast` is the performance-oriented leaf insertion variant used by later insert code.

The chunk ends with `NN` and `NB`, which define the three-page neighborhood used by the balancing algorithms that follow. The `CellArray` comment establishes the data model for redistributing cells across parent and sibling pages but the implementation is outside this chunk.

## State And Persistence Behavior

Persistent database state touched by this chunk includes:

- Page 1 database header fields: magic header, page size, read/write format versions, reserved bytes, payload fractions, change/schema metadata, database page count at offset 28, first free-list trunk at offset 32, free page count at offset 36, and auto-vacuum metadata fields.
- B-tree pages: type flags, first freeblock, cell count, cell-content start, fragmented byte count, right-child pointer for internal pages, cell pointer array, local cell payload, and overflow page pointers.
- Overflow pages: 4-byte next-page pointer followed by payload bytes.
- Free-list trunk and leaf pages: trunk next pointer, leaf count, and leaf page-number array.
- Pointer-map pages in auto-vacuum databases: ownership records that allow page relocation during vacuum.
- Pager transaction state: rollback journal/WAL locks, savepoints, dirty pages, page-cache references, page-size settings, mmap limits, synchronous flags, and busy-handler callbacks.

Transient state includes cursor page stacks, saved cursor keys, cursor cell-info caches, overflow-chain caches, shared-cache table lock lists, temp cell-construction space, `pHasContent` rollback-safety bitvecs, and `BtShared.pPage1` read-lock references. Transaction cleanup clears or releases these structures depending on commit, rollback, cursor close, or btree close paths.

The code is careful about when content can be skipped. Free-list leaf pages often have meaningless content, so no-content pager reads/writes are used for performance. The `pHasContent` bitvec disables that optimization for pages that were freed after containing real data in the current transaction, preserving rollback correctness.

## Dependencies And Integration Points

This chunk depends on SQLite internal subsystems rather than external libraries:

- Pager APIs: `sqlite3PagerOpen`, `sqlite3PagerGet`, `sqlite3PagerLookup`, `sqlite3PagerWrite`, `sqlite3PagerBegin`, `sqlite3PagerRollback`, `sqlite3PagerCommitPhaseOne`, `sqlite3PagerCommitPhaseTwo`, `sqlite3PagerOpenSavepoint`, `sqlite3PagerSavepoint`, `sqlite3PagerMovepage`, `sqlite3PagerTruncateImage`, `sqlite3PagerPagecount`, `sqlite3PagerSetPagesize`, cache/mmap/spill/sync configuration, WAL open/write-lock helpers, and direct-read checks.
- VFS/file APIs: full-path canonicalization, file-control hints, file reads for direct overflow access, and pending-byte page calculations.
- Memory and utility APIs: SQLite allocators, page allocators, bitvecs, varint helpers, endian helpers, hash traversal for schema/index lookup, fault injection, corruption reporting, and test/debug macros.
- VDBE record APIs: `sqlite3VdbeAllocUnpackedRecord`, `sqlite3VdbeRecordUnpack`, `sqlite3VdbeFindCompare`, `sqlite3VdbeRecordCompare`, and record comparison error propagation for index searches.
- Schema and database connection state: `Schema`, `Index`, shared-cache flags, read-uncommitted flag, reset-database flag, autovacuum callback, savepoint count, active VDBE readers, writable-schema mode, busy handler, mmap setting, and pager flag mask.

The btree layer integrates upward with table/index opcodes, schema management, blob I/O, savepoint/transaction SQL, autovacuum pragmas, secure-delete pragmas, cache/mmap/page-size pragmas, shared-cache mode, and integrity/corruption reporting. It integrates downward with the pager, WAL/rollback journal machinery, the VFS, and the database file format.

## Risks And Edge Cases

The highest-risk behavior in this chunk is file-format and transaction correctness. Payload local/overflow split calculations, page header offsets, freeblock accounting, pointer-map updates, and page-1 metadata writes are format-defining; small changes can make databases unreadable or corrupt under rollback.

Shared-cache locking is another sensitive area. The code assumes one writer per shared cache, schema-root lock semantics, table-level conflict detection, and careful lock downgrade/removal at transaction end. Incorrect changes can produce missed `SQLITE_LOCKED_SHAREDCACHE` errors or cross-connection visibility bugs.

Cursor restoration is fragile because structural changes can move or delete the current row. The saved-key path must handle table and index cursors differently, avoid pinned cursors, release page references, and correctly report when a cursor restored to a nearby row rather than the same row.

Overflow handling has multiple corruption and safety risks: overflow chains may be truncated, point beyond `nPage`, overlap live pages, or be misinterpreted in auto-vacuum mode if pointer-map entries are stale. The code defends by validating page ranges, using pointer-map fallbacks, checking page reference counts before freeing, and clearing overflow caches after writes, vacuum, or cursor moves.

Auto-vacuum relocation is especially interdependent. Moving a page requires updating the moved page's children, the parent or previous overflow page that pointed to it, and pointer-map records for all affected pages. Missing one update can produce a database that appears valid until later vacuum, delete, or integrity-check work.

Free-list manipulation must preserve historical compatibility and rollback semantics. Reusing or freeing a page with `PAGER_GET_NOCONTENT` is only safe when the previous content is irrelevant or recoverable. The `pHasContent` bitvec exists specifically to avoid a rollback data-loss corner case when a page is freed and reused in the same transaction.

Several fast paths intentionally trade complexity for performance: direct local index-key comparison, current-key table seek optimization, leaf-page next/previous movement, defragmentation fast path, direct overflow file reads, and no-content page fetches. These paths need to stay equivalent to slower fallbacks.

## Test Signals

Useful validation signals for this chunk include:

- B-tree format and corruption tests that exercise malformed page headers, invalid cell offsets, bad freeblock chains, impossible payload sizes, short overflow chains, invalid root page types, out-of-range page numbers, and bad pointer-map entries.
- Transaction tests covering read/write/exclusive begin, busy and locked behavior, rollback after cursor movement, statement savepoint rollback, full commit, two-phase commit, read transaction downgrade, and reset-database handling.
- Shared-cache tests with multiple connections, read-uncommitted readers, schema locks, table locks, writer conflicts, exclusive transactions, and cursor conflicts.
- Page-size and header tests for new databases, existing databases, 512 through 65536 byte pages, reserved bytes, WAL read/write versions, invalid magic headers, and page-size changes before and after `BTS_PAGESIZE_FIXED`.
- Cursor tests for first/last/next/previous, table rowid seek, index seek with local and overflow keys, empty trees, virtual root page behavior, cursor restoration after insert/delete/rebalance, pinned cursor constraints, and row-count estimates.
- Payload tests for local-only records, records spanning many overflow pages, incremental blob reads, direct payload fetches, payload writes, zero-filled payload tails, direct overflow reads, and overflow-cache invalidation.
- Free-list and allocation tests that allocate from empty databases, free and reuse pages in one transaction, allocate exact pages during auto-vacuum, skip pending-byte and pointer-map pages, detect corrupt trunk/leaf counts, and preserve rollback behavior.
- Auto-vacuum tests for incremental vacuum, full autovacuum on commit, page relocation of b-tree and overflow pages, pointer-map repair, autovacuum callback-limited truncation, and interactions with cursor saving.
- Secure-delete tests confirming in-page freed content and, in full secure-delete mode, freed pages are zeroed without breaking free-list structure.

SQLite's own debug, fault-injection, and test-only assertions are important test signals here: `SQLITE_DEBUG` shared-lock checks, `cell_size_check`, `sqlite3FaultSim` paths, `testcase()` annotations, pager reference-count assertions, and `CORRUPT_DB` conditional assertions all identify behavior that should be covered by TH3, dbsqlfuzz, sqllogictest, and SQLite's TCL test suite.

### subset-b-008766: lines 7569-11600

# sources/storage-engines/sqlite/src/btree.c lines 7569-11600

## Scope

This chunk covers the late btree implementation in SQLite's `btree.c`. It starts inside the `CellArray` balancing data structure comments and includes page reconstruction, sibling balancing, root-depth adjustments, insert/delete paths, table creation/drop/clear helpers, btree metadata access, row counting, integrity checking, and small public utility APIs for filenames, WAL checkpointing, schema storage, shared-cache locking, incremental blob writes, file-format version changes, and cache clearing.

The code is write-path critical. Most routines assume the caller already owns the btree mutex and, for mutations, has a write transaction plus writable pager pages. Error returns from balancing and page relocation usually imply the pager transaction must roll back to avoid a half-mutated btree image.

## Purpose

The main purpose of this range is to maintain btree structural invariants while records are inserted, overwritten, deleted, tables are created/dropped, or integrity checks traverse the database. It handles:

- Redistributing cells across sibling pages after overfull or underfull page mutations.
- Growing or shrinking tree height via root split (`balance_deeper`) and root collapse (`balance_nonroot` shallower path).
- Preserving cell ordering, page free space, overflow-cell ownership, and parent divider cells during balancing.
- Creating and freeing root pages, including auto-vacuum pointer-map and largest-root-page metadata rules.
- Clearing table contents and overflow chains safely.
- Validating full database structure with `sqlite3BtreeIntegrityCheck`.
- Exposing btree-level utility hooks used by pager, schema, WAL, shared-cache, incremental blob, and VDBE layers.

## Important APIs, Types, and Functions

The central local type is `CellArray`. It is a transient view over an ordered sequence of btree cells gathered from up to three sibling pages plus parent divider cells. `apCell[]` points to cells, `szCell[]` caches cell sizes, `pRef` supplies common page parsing callbacks, and `apEnd[]`/`ixNx[]` track the source page boundaries used to detect corrupt overlapping source buffers while cells are copied.

Important balancing helpers:

- `populateCellCache()`, `computeCellSize()`, and `cachedCellSize()` lazily compute cell sizes through `MemPage.xCellSize`.
- `rebuildPage()` reconstructs a page from a `CellArray`, copying self-referential cells through pager temp space and resetting the page header, cell pointer array, fragmented-byte count, `nCell`, and `nOverflow`.
- `pageInsertArray()` incrementally inserts cell-array entries into an existing page, preferably using free slots from `pageFindSlot()`, and reports failure if defragmentation/rebuild is needed.
- `pageFreeArray()` adds existing page-resident cells back to the page free list, coalescing adjacent ranges before calling `freeSpace()`.
- `editPage()` transforms one sibling page from its old slice of the cell array to its new slice, falling back to `rebuildPage()` if in-place editing cannot fit or detects corruption.
- `balance_quick()` handles the append-only rightmost table-leaf special case by allocating a new right sibling, moving the single overflow cell there, and inserting a divider in the parent.
- `copyNodeContent()` copies a node image from one page to another and reinitializes child/overflow pointer maps for auto-vacuum.
- `balance_nonroot()` is the main sibling redistribution algorithm. It gathers old sibling cells and parent dividers, chooses page counts and per-page cell counts, allocates/reuses sibling pages, rekeys page numbers into ascending order, updates pointer maps, inserts new parent dividers, edits sibling pages in dependency-safe order, collapses an empty root when possible, and frees old pages not reused.
- `balance_deeper()` handles an overfull root by allocating a new child, copying the old root into it, installing it as the root right-child, and moving overflow-cell arrays to the child.
- `balance()` dispatches among quick, deeper, and non-root balancing while walking upward toward the root.

Important mutation APIs:

- `sqlite3BtreeInsert()` inserts or replaces a table row or index key. It saves other cursors when needed, seeks if no adjacent cursor position is supplied, uses same-size overwrite optimizations, formats cells through `fillInCell()` or preformatted transfer data, calls `insertCellFast()`, then invokes `balance()` if the page overflows.
- `btreeOverwriteContent()`, `btreeOverwriteOverflowCell()`, and `btreeOverwriteCell()` update same-size payload content in place, including overflow pages, avoiding pager writes when bytes are unchanged.
- `sqlite3BtreeTransferRow()` preformats a cell in the destination btree's temp buffer by copying local and overflow payload from a source cursor, allocating destination overflow pages as required.
- `sqlite3BtreeDelete()` removes the current cursor entry, optionally preserves cursor position, replaces internal-node cells with the predecessor leaf cell, clears overflow chains, drops page cells, and balances the affected leaf/internal paths.

Table and metadata APIs:

- `btreeCreateTable()` / `sqlite3BtreeCreateTable()` allocate and initialize a new root page. In auto-vacuum mode, they keep root pages dense before pointer-map pages and the pending-byte page, relocating an existing page if necessary.
- `clearDatabasePage()`, `sqlite3BtreeClearTable()`, and `sqlite3BtreeClearTableOfCursor()` recursively clear a btree, free child pages and overflow chains, and leave the root page empty when requested.
- `btreeDropTable()` / `sqlite3BtreeDropTable()` clear a table and free its root. In auto-vacuum mode, dropping a non-largest root relocates the largest root page into the gap and updates meta slot 4 (`BTREE_LARGEST_ROOT_PAGE`).
- `sqlite3BtreeGetMeta()` reads database header meta slots, with `BTREE_DATA_VERSION` delegated to the pager data-version counter.
- `sqlite3BtreeUpdateMeta()` writes database header meta slots and updates `BtShared.incrVacuum` when `BTREE_INCR_VACUUM` changes.
- `sqlite3BtreeCount()` traverses all btree pages with a cursor and counts entries, honoring connection interrupts.

Integrity and utility APIs:

- `sqlite3BtreeIntegrityCheck()` orchestrates full or partial integrity checks over root pages, freelist, overflow chains, pointer maps, page coverage, row order, page references, and row counts.
- `checkTreePage()`, `checkList()`, `checkRef()`, `checkPtrmap()`, `btreeHeapInsert()`, and `btreeHeapPull()` implement recursive validation and page byte-coverage checks.
- `sqlite3BtreePager()`, `sqlite3BtreeGetFilename()`, `sqlite3BtreeGetJournalname()`, `sqlite3BtreeTxnState()`, `sqlite3BtreeCheckpoint()`, `sqlite3BtreeIsInBackup()`, `sqlite3BtreeSchema()`, `sqlite3BtreeSchemaLocked()`, `sqlite3BtreeLockTable()`, `sqlite3BtreePutData()`, `sqlite3BtreeIncrblobCursor()`, `sqlite3BtreeSetVersion()`, `sqlite3BtreeCursorHasHint()`, `sqlite3BtreeIsReadonly()`, `sqlite3HeaderSizeBtree()`, `sqlite3BtreeClearCache()`, `sqlite3BtreeSharable()`, and `sqlite3BtreeConnectionCount()` expose btree state and integration hooks to the rest of SQLite.

## Control Flow

Insertion starts by stabilizing cursor state. `sqlite3BtreeInsert()` saves peer cursor positions when the cursor can share a root with others, restores or seeks the cursor unless an adjacent position was supplied, invalidates incremental-blob cursors for table rows being replaced, and chooses between overwrite and delete-plus-insert. A same-size payload can be rewritten in place with `btreeOverwriteCell()`. Otherwise the old cell is cleared/dropped, a new cell is assembled in `BtShared.pTmpSpace`, inserted with `insertCellFast()`, and `balance()` is called if the target page now has overflow cells.

`balance()` loops upward. If a page has no overflow and less than or equal to two-thirds free space, it stops. If the root is overfull, it calls `balance_deeper()` once to copy root content into a new child and then balances that child on the next iteration. For non-root pages, it writes the parent, uses `balance_quick()` for the single rightmost append case, otherwise allocates a scratch page buffer and calls `balance_nonroot()`. After each non-root balance it releases the child page and moves the cursor to the parent because the parent may now be overfull or underfull.

`balance_nonroot()` has the densest control flow. It selects up to `NB` old siblings around the target child, removes their divider cells from the parent, gathers all sibling cells and relevant divider cells into `CellArray`, and computes a new packing. The first packing pass may bias cells left; a second pass shifts cells right to avoid empty or badly underfilled right siblings. It allocates or reuses new sibling pages, reorders page numbers for better scan locality, updates auto-vacuum pointer maps for moved cells and overflow chains, inserts new divider cells into the parent, then updates each sibling page in an order that avoids overwriting source cells before they have been copied. If the parent is the root and becomes empty with one child, it defragments the child, copies it into the parent, and frees the child to reduce tree height.

Deletion starts in `sqlite3BtreeDelete()`. If position preservation is requested and balancing may happen, the key is saved into `CURSOR_REQUIRESEEK` state. Internal-node deletion first moves to the predecessor leaf entry, then the leaf cell is inserted into the internal node with the appropriate child pointer before the leaf copy is dropped. The affected page is balanced only if free space exceeds the two-thirds threshold. If an internal-node replacement left the cursor below the original depth, the code climbs back and balances the original internal level as well.

Table creation and drop integrate page allocation with auto-vacuum invariants. Creation chooses the next largest root page, skipping pointer-map and pending-byte pages, then may relocate the page currently occupying that root slot. Drop clears the table first, then either frees the largest root or moves the largest root into the dropped root slot and decrements the largest-root metadata while skipping reserved pages.

Integrity checking allocates a bitset for referenced pages plus a page-sized heap. It optionally checks the freelist, then recurses into each requested root through `checkTreePage()`. That routine reinitializes each page to exercise corruption checks, validates cell offsets and payload/overflow chains, checks rowid ordering, recurses through child pointers, verifies child depths match, then uses a min-heap of cell and freeblock byte ranges to detect overlap and fragmentation-count mismatches. A final full check reports unreferenced pages and pointer-map pages that were incorrectly referenced.

## State and Persistence Behavior

Balancing mutates persistent page images through pager-managed dirty pages. It rewrites btree page headers, cell pointer arrays, cell content areas, freeblock chains, fragmented-byte counters, right-child pointers, parent divider cells, and overflow-chain pointer maps. `MemPage.nFree` is deliberately invalid after low-level page editing until the caller resets it from computed sizes.

The pager is the durability boundary. Mutating functions call `sqlite3PagerWrite()` or operate only on pages already made writable. If a balancing or pointer-map update fails after page content has been changed, the transaction must roll back; comments in this range explicitly rely on rollback for partially mutated parent/sibling state.

Auto-vacuum adds persistent pointer-map and metadata state. New btree pages, moved root pages, child pointers, overflow first pages, overflow continuation pages, free pages, and root pages must all have correct pointer-map entries. `BTREE_LARGEST_ROOT_PAGE` in page-1 metadata is updated during create/drop, and `BTREE_INCR_VACUUM` updates both the file header and `BtShared.incrVacuum`.

Cursor state is heavily managed. Insert/delete may invalidate cursor page stacks, save keys for later reseek, leave a cursor in `CURSOR_SKIPNEXT`, or release all cursor pages after balancing. Incremental blob cursors are invalidated when their row may be replaced, deleted, or a table is cleared. Overflow cache entries are invalidated when pages might be relocated or overflow chains changed.

Integrity checking is mostly read-only but temporarily clears and restores `MemPage.isInit` to force page validation. It also temporarily clears `SQLITE_CellSizeCk` from database flags while scanning, accumulates error text in a `StrAccum`, and writes per-root row counts into caller-provided `Mem` values.

Small utility routines expose or mutate shared btree state: `sqlite3BtreeSchema()` allocates `BtShared.pSchema` and records its destructor; `sqlite3BtreeSetVersion()` writes header bytes 18 and 19 and temporarily sets `BTS_NO_WAL` when forcing rollback-journal format; `sqlite3BtreeClearCache()` asks the pager to drop cache only when no transaction is active.

## Dependencies and Integration Points

This chunk depends on earlier `btree.c` machinery: `MemPage`, `BtShared`, `BtCursor`, `CellInfo`, `BtreePayload`, page parsing callbacks, `findCell()`, `insertCell()`, `insertCellFast()`, `dropCell()`, `freeSpace()`, `defragmentPage()`, `zeroPage()`, `fillInCell()`, `clearCell`, `allocateBtreePage()`, `freePage()`, `relocatePage()`, cursor navigation, and shared-cache lock helpers.

Pager integration is pervasive. The code uses pager temp space, page refcounts, `sqlite3PagerWrite()`, `sqlite3PagerRekey()`, `sqlite3PagerGet()`, `sqlite3PagerUnref()`, `sqlite3PagerFilename()`, `sqlite3PagerJournalname()`, `sqlite3PagerCheckpoint()`, `sqlite3PagerDataVersion()`, `sqlite3PagerRefcount()`, and cache clearing. Page refcount checks are treated as corruption signals in balancing and clearing when a page appears as its own ancestor or is unexpectedly held.

Auto-vacuum integration is through `ptrmapPut()`, `ptrmapGet()`, `ptrmapPutOvflPtr()`, `setChildPtrmaps()`, `PTRMAP_*` types, `PTRMAP_PAGENO()`, and `PTRMAP_ISPAGE()`. Correctness here affects vacuum, page relocation, and corruption detection.

Higher SQLite layers call the public `sqlite3Btree*` APIs from VDBE opcodes, schema management, pager/WAL control, backup handling, incremental blob APIs, and shared-cache table locking. The insert/delete paths rely on VDBE-provided flags such as `BTREE_APPEND`, `BTREE_SAVEPOSITION`, `BTREE_PREFORMAT`, and `BTREE_AUXDELETE`.

Compile-time feature gates shape behavior: `SQLITE_OMIT_QUICKBALANCE`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_INTEGRITY_CHECK`, `SQLITE_OMIT_WAL`, `SQLITE_OMIT_SHARED_CACHE`, and `SQLITE_OMIT_INCRBLOB` include or remove significant branches.

## Risks

- `balance_nonroot()` is high risk because it changes parent and sibling pages together. Off-by-one errors in `cntNew`, `cntOld`, `leafCorrection`, or divider-cell handling can break key ordering or child ownership.
- Source/destination overlap is a recurring corruption hazard. `CellArray.apEnd`/`ixNx`, temp-space copies, and careful page edit ordering protect against reading cells after their source page is overwritten.
- `MemPage.nFree` must be recomputed or explicitly assigned after low-level edits. Using stale free-space values can skip required balancing or corrupt later insertions.
- Auto-vacuum pointer-map updates are security- and durability-sensitive. Missing updates after page rekeying, overflow-chain allocation, table create/drop, root collapse, or transfer-row overflow allocation can make later vacuum relocate the wrong page or report corruption.
- Same-size overwrite optimizations deliberately bypass full drop/insert. They are safe only when payload sizes and local/overflow conditions match and when auto-vacuum does not require a new overflow pointer-map entry.
- Cursor preservation is subtle. Insert/delete can leave cursors invalid, require reseek, or use skip-next semantics; missing a state transition can make subsequent VDBE cursor movement skip or duplicate rows.
- Table create/drop in auto-vacuum mode relocates real pages to keep root pages packed. Errors in reserved-page skipping or largest-root metadata updates can make the database structurally inconsistent.
- Integrity checking recurses through database-controlled page numbers and must cap errors, detect duplicate references, and avoid trusting initialized `MemPage` state from prior use.
- Several routines treat unexpected pager refcounts as corruption. Changes in pager ownership or cursor lifetime rules must keep these assumptions aligned.

## Test and Validation Signals

Useful validation for this chunk includes:

- SQLite btree insert/delete regression tests with random rowid inserts, append-heavy inserts, index inserts, replacements with same-size and different-size payloads, and large payloads using overflow pages.
- Delete tests that remove internal-node separator keys, delete from underfull pages, preserve cursor positions, and exercise `BTREE_SAVEPOSITION`.
- Auto-vacuum and incremental-vacuum tests that create/drop many tables, relocate root pages, allocate/free overflow pages, and run `PRAGMA integrity_check` after each phase.
- Fuzz and corruption tests that target malformed cell offsets, overlapping cells/freeblocks, bad overflow chains, duplicate page references, bad pointer maps, and page refcount anomalies.
- `PRAGMA integrity_check` and `quick_check` coverage for full checks and partial single-table checks, including databases with freelist pages, pointer-map pages, overflow chains, and mixed rowid/WITHOUT ROWID trees.
- WAL checkpoint tests verifying `sqlite3BtreeCheckpoint()` returns `SQLITE_LOCKED` while a shared btree transaction is active and delegates to pager checkpointing otherwise.
- Incremental blob tests that write fixed-length blob slices, reject invalid cursor states, and verify row replacement/delete/table clear invalidates active blob cursors.
- Header metadata tests around schema cookies, data version, largest root page, incremental-vacuum flag, and `sqlite3BtreeSetVersion()` transitions between rollback and WAL file-format version bytes.
- Interrupt/progress tests for `sqlite3BtreeCount()` and integrity checking to verify `SQLITE_INTERRUPT` propagation and bounded error reporting.
