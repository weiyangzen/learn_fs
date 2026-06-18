# Research: sources/storage-engines/foundationdb/contrib/sqlite/btree.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008403`: lines 1-7896, `Docs/researches/chunks/subset-b-008403_research.md`
- `subset-b-008404`: lines 7897-8795, `Docs/researches/chunks/subset-b-008404_research.md`

## Chunk Research

### subset-b-008403: lines 1-7896

# sources/storage-engines/foundationdb/contrib/sqlite/btree.c lines 1-7896

## Scope And Purpose

This chunk implements almost all of SQLite's disk-backed b-tree layer as vendored under FoundationDB's SQLite integration. It sits between the SQL/VDBE layer and the pager layer, translating table/index cursor operations into page reads, page writes, cell layout changes, overflow-page management, freelist updates, auto-vacuum pointer-map maintenance, and transaction/savepoint boundaries.

The covered range starts at the file header and runs through metadata update and the beginning of `sqlite3BtreeCount()`. It excludes the later integrity-check and auxiliary tail of the file, but includes the operational core: open/close, shared-cache table locks, page decoding, cursor positioning, payload access, page allocation/freeing, insert/delete, balancing, lazy delete/range delete additions, table create/clear/drop, and b-tree metadata access.

This copy is not a byte-for-byte upstream SQLite file. FoundationDB-specific or nonstandard changes are visible in the database-open page-size handling, disabled/altered pointer-map traversal checks, augmented freelist pointer-map states, partial index-record comparison, and added lazy-delete/range-delete APIs.

## Important APIs, Types, And Functions

Public b-tree entry points in this chunk include `sqlite3_enable_shared_cache`, `sqlite3BtreeOpen`, `sqlite3BtreeClose`, `sqlite3BtreeBeginTrans`, `sqlite3BtreeCommitPhaseOne`, `sqlite3BtreeCommitPhaseTwo`, `sqlite3BtreeCommit`, `sqlite3BtreeRollback`, `sqlite3BtreeBeginStmt`, `sqlite3BtreeSavepoint`, `sqlite3BtreeCursor`, `sqlite3BtreeCloseCursor`, `sqlite3BtreeFirst`, `sqlite3BtreeLast`, `sqlite3BtreeMovetoUnpacked`, `sqlite3BtreeNext`, `sqlite3BtreePrevious`, `sqlite3BtreeInsert`, `sqlite3BtreeDelete`, `sqlite3BtreeCreateTable`, `sqlite3BtreeClearTable`, `sqlite3BtreeDropTable`, `sqlite3BtreeGetMeta`, and `sqlite3BtreeUpdateMeta`.

The core local types are defined elsewhere but used throughout: `Btree` is the connection-local handle, `BtShared` is the shared pager/cache state, `BtCursor` tracks a cursor stack of `MemPage` references and cell indexes, `MemPage` is the b-tree view of a pager page, `CellInfo` caches decoded cell layout, and `BtLock` represents shared-cache table locks.

Shared-cache locking is handled by `querySharedCacheTableLock`, `setSharedCacheTableLock`, `clearAllSharedCacheTableLocks`, `downgradeAllSharedCacheTableLocks`, and debug-only `hasSharedCacheTableLock`/`hasReadConflicts`. These enforce one writer per shared b-tree and table-level read/write compatibility between `Btree` handles.

Page and cell primitives include `btreeParseCellPtr`, `cellSizePtr`, `defragmentPage`, `allocateSpace`, `freeSpace`, `decodeFlags`, `btreeInitPage`, `zeroPage`, `btreeGetPage`, `getAndInitPage`, `releasePage`, and `pageReinit`. Together these validate on-disk page headers, maintain cell pointer arrays and freeblocks, and keep `MemPage` metadata synchronized with pager data.

Cursor and payload routines include `saveCursorPosition`, `saveAllCursors`, `btreeMoveto`, `btreeRestoreCursorPosition`, `sqlite3BtreeCursorHasMoved`, `accessPayload`, `sqlite3BtreeKey`, `sqlite3BtreeData`, `sqlite3BtreeKeyFetch`, `sqlite3BtreeDataFetch`, `moveToRoot`, `moveToChild`, `moveToParent`, `moveToLeftmost`, and `moveToRightmost`. These preserve cursor semantics while tree pages are modified, support direct local payload access, and traverse overflow chains when payload spills off-page.

Write-path page management is centered on `allocateBtreePage`, `freePage2`, `freePage`, `clearCell`, `fillInCell`, `dropCell`, `insertCell`, `assemblePage`, `balance_quick`, `balance_nonroot`, `balance_deeper`, and `balance`. These functions allocate cells and overflow pages, release overflow chains, manipulate freelist trunks/leaves, split or merge pages, and propagate balancing up toward the root.

Auto-vacuum and pointer-map support is handled by `ptrmapPageno`, `ptrmapPut`, `ptrmapGet`, `ptrmapPutOvflPtr`, `setChildPtrmaps`, `modifyPagePointer`, `relocatePage`, `incrVacuumStep`, `sqlite3BtreeIncrVacuum`, and `autoVacuumCommit`. This chunk adds `PTRMAP_LAZYFREE` and distinguishes `PTRMAP_FREEPAGE` from `PTRMAP_FREELEAF` in several freelist paths.

FoundationDB-added deletion helpers include `sqlite3BtreeLazyDelete`, `deleteCellRange`, `swapChildren`, and `sqlite3BtreeDeleteRange`. They use an integer stack and a cursor-backed lazy-free table to delete whole page subtrees incrementally rather than synchronously walking and freeing all descendant pages in one call.

## Control Flow

Opening starts in `sqlite3BtreeOpen`. It creates a `Btree`, optionally attaches to an existing `BtShared` via shared cache, otherwise opens a pager and reads the first 100-byte database header. This version deliberately sets `pBt->pageSize = 0` instead of trusting a valid-looking initial header field, with comments explaining that a correct page 1 may exist in WAL and a checksumming pager codec can fail if initialized with a corrupt stale header's page size. `lockBtree` later reads page 1 through the pager, validates the magic header and format bytes, opens WAL if required, adjusts page size/reserve size, computes local payload thresholds, and pins `pBt->pPage1`.

Transactions flow through `sqlite3BtreeBeginTrans`. It checks read-only and shared-cache conflicts, obtains a page-1 read lock, repeatedly calls `lockBtree` until page 1 is initialized, begins the pager write transaction for write cases, creates a new database image if the file is empty, updates `Btree`/`BtShared` transaction state, and ensures pager savepoint slots match the connection's active savepoints. Commit phase one optionally runs full auto-vacuum compaction before `sqlite3PagerCommitPhaseOne`; phase two commits the pager and calls `btreeEndTransaction` to clear locks, free `pHasContent`, downgrade or close transactions, and release page 1 when no cursors remain. Rollback saves/trips cursors, rolls the pager back, reloads page count from page 1, and ends the transaction.

Cursor open and movement are layered. `btreeCursor` links a zeroed cursor into `BtShared.pCursor` after checking lock and transaction invariants. `moveToRoot` positions on the root or virtual root, verifies expected table/index page type, and marks empty trees invalid. `sqlite3BtreeMovetoUnpacked` performs a binary search on each page, comparing integer rowids directly for table b-trees and unpacked records for index b-trees, then descends through child pointers until a leaf or exact match is found. `sqlite3BtreeNext` and `sqlite3BtreePrevious` restore deferred cursor positions, step within the current page, and walk up/down the page stack as needed.

Payload reads and writes start with decoded `CellInfo`. If requested bytes are local, `copyPayload` reads or writes the page directly. If bytes spill to overflow pages, `accessPayload` follows the overflow chain, optionally using `BtCursor.aOverflow` for incremental blob cursors. The pointer-map shortcut in `getOverflowPage` is compiled out in this copy, and comments say traversal should validate child-parent links; however `verifyParentChildLink` itself is currently compiled as a no-op macro, so that intended validation is not active in this chunk.

Insertion calls `saveAllCursors`, seeks if the caller did not provide a prior search result, builds the new cell with `fillInCell`, deletes the old cell on replace, inserts the new cell or records it as an overflow cell, and calls `balance` if the page overflowed. `fillInCell` writes the cell header, decides local versus overflow payload bytes, allocates overflow pages, links overflow pages together, and populates pointer-map entries for auto-vacuum databases.

Deletion in `sqlite3BtreeDelete` verifies a writable cursor, invalidates incremental blob cursors, replaces internal-node cells with predecessor leaf cells when needed, frees overflow pages with `clearCell`, drops the cell from the page, and calls `balance` on the affected leaf and possibly the original internal node. `balance` chooses between root deepening, quick right-edge split, or full non-root sibling redistribution. `balance_nonroot` collects cells from up to three siblings plus parent dividers, repacks them into old or newly allocated pages, frees unused pages, inserts new divider cells, and repairs pointer-map entries for moved children and overflow chains.

Table creation, clearing, and dropping are page-management wrappers. `btreeCreateTable` allocates a root page, moves pages as needed in auto-vacuum mode so root pages remain compact, marks the root in pointer-map metadata, updates largest-root metadata, and initializes the page as either intkey table or zerodata index. `clearDatabasePage` recursively clears cells, overflow chains, and child pages. `btreeDropTable` clears the table, frees or moves root pages, and updates largest-root metadata when auto-vacuum is enabled.

## State And Persistence Behavior

Persistent database state is stored in pager pages. Page 1 contains the file header, page count at offset 28, freelist trunk pointer/count at offsets 32 and 36, and metadata slots beginning at offset 36. This chunk reads and writes those fields through `get4byte`/`put4byte` and always marks page 1 writable before mutating them.

Each b-tree page stores a compact on-disk header, a cell pointer array, cell content at the end of the usable page region, and a linked list of freeblocks. `btreeInitPage` reconstructs volatile `MemPage` fields from that image. `dropCell`, `insertCell`, `freeSpace`, `allocateSpace`, and `defragmentPage` update both the raw bytes and `MemPage` counters such as `nCell`, `nFree`, and `nOverflow`.

Overflow payload is persisted as linked overflow pages with the next-page number in the first four bytes. `clearCell` must free every overflow page when a cell is deleted or replaced. `fillInCell` must write all overflow links before the new cell is installed. In auto-vacuum mode, first overflow pages are recorded as `PTRMAP_OVERFLOW1` and subsequent pages as `PTRMAP_OVERFLOW2`.

The freelist is stored as trunk pages with arrays of leaf page numbers. `freePage2` increments the free count and either appends a page as a leaf of the first trunk or makes it the new trunk. `allocateBtreePage` decrements the count and reuses a requested or nearby free page where possible, otherwise extends the file and skips pointer-map or pending-byte pages. This copy adds logic for truncated freelist leaves and pointer-map entries that can point from free leaves to their parent trunk.

`BtShared.pHasContent` is a transaction-local bitvec that records pages that had meaningful content before becoming freelist leaves. It prevents no-content pager optimizations from making rollback unable to restore a page that is freed and then reused in the same transaction. It is cleared at transaction end.

Auto-vacuum persistence depends on pointer-map pages. `relocatePage` moves a page at the pager layer, updates child pointer-map entries, and rewrites the parent pointer that referenced the old page number. `autoVacuumCommit` repeatedly moves pages out of the tail of the file, clears the freelist, truncates the pager image, and updates page count.

Cursor state is partly persistent only by reference: cursors hold page references and cell indexes but do not persist to disk. Before structural mutations, `saveAllCursors` stores keys for other valid cursors and releases page references so they can be restored later with `btreeRestoreCursorPosition`.

`sqlite3BtreeLazyDelete` persists pending subtree roots in a cursor table as integer payloads keyed by monotonically increasing rowids. It also marks roots in pointer-map entries as `PTRMAP_LAZYFREE` so vacuum/allocation code can recognize lazily freed pages.

## Dependencies And Integration Points

The b-tree layer depends heavily on the pager API: `sqlite3PagerOpen`, `sqlite3PagerAcquire`, `sqlite3PagerGet`, `sqlite3PagerWrite`, `sqlite3PagerBegin`, `sqlite3PagerCommitPhaseOne`, `sqlite3PagerCommitPhaseTwo`, `sqlite3PagerRollback`, `sqlite3PagerMovepage`, `sqlite3PagerTruncateImage`, WAL open/checkpoint behavior, page refcounts, and pager temp/scratch space.

It integrates with SQLite connection state through `sqlite3`, database mutexes, busy handlers, `sqlite3GlobalConfig.sharedCacheEnabled`, VFS lookup, savepoint counts, active VDBE counts, read-uncommitted flags, and memory allocation failure propagation.

The VDBE/index layer integrates through cursor APIs, key/data fetch APIs, `UnpackedRecord`, `KeyInfo`, `sqlite3VdbeRecordUnpack`, `sqlite3VdbeRecordCompare`, and `sqlite3VdbeDeleteUnpackedRecord`. This copy's `sqlite3BtreeMovetoUnpacked` adds a partial-record comparison path for overflow index keys: it compares local bytes first and only loads full payload if the comparator reports that more data is required.

Shared-cache integration uses connection-blocking diagnostics via `sqlite3ConnectionBlocked` and table-level locks rooted at page numbers. Schema/index assertions in debug builds use `Schema`, `Index`, and SQLite hash iteration to verify that index writes hold locks on the owning table root.

Auto-vacuum integration depends on file-format metadata, pointer-map page placement, `PENDING_BYTE_PAGE`, and root-page compaction rules. Table create/drop paths update `BTREE_LARGEST_ROOT_PAGE`; metadata APIs read/write the schema-layer cookies and incremental-vacuum flag.

Incremental blob support integrates through cursor flags and overflow-cache invalidation. Any table modification, auto-vacuum move, create table, or full auto-vacuum commit can invalidate open incremental blob cursors or their cached overflow lists.

FoundationDB integration signals are visible in comments and APIs rather than direct FoundationDB calls in this chunk. The b-tree remains pager-backed SQLite code, but with modifications likely serving FoundationDB's SQLite storage semantics: cautious page-size initialization for WAL/codecs, augmented pointer-map expectations (`g_expect_full_pointermap`), lazy-free state, and range deletion helpers.

## Risks And Edge Cases

Page-format corruption handling is pervasive and security-sensitive. Many routines return `SQLITE_CORRUPT_BKPT` on impossible offsets, invalid freeblock chains, too many cells, overflow pages outside the file, root-page misuse, incompatible page flags, or pointer-map inconsistencies. Small mistakes in cell-size calculation, freeblock coalescing, or pointer-array movement can corrupt the database image.

The disabled `verifyParentChildLink` is a notable risk. Comments in `getOverflowPage`, `accessPayload`, `moveToChild`, and `clearCell` describe validating child-parent links before following pointers, but the helper is compiled out. If FoundationDB relies on full pointer-map validation, this chunk does not currently enforce it.

Pointer-map state is more complex than upstream SQLite because `PTRMAP_FREELEAF` and `PTRMAP_LAZYFREE` are accepted in addition to normal states. `allocateBtreePage`, `incrVacuumStep`, and lazy delete must agree on these values. A stale or partially populated pointer map can cause wrong freelist searches, premature vacuum completion, or allocation of the wrong page.

`allocateBtreePage` has high blast radius. It mutates page-1 freelist count before walking trunks, may skip to a parent trunk using pointer-map data, compacts truncated leaves, can promote a freelist leaf into a trunk, and must release every page reference along error paths. Regression here can leak pages, double-allocate pages, or leave the freelist count inconsistent with its trunk chain.

Balancing is another high-risk area. `balance_nonroot` relies on scratch memory layouts, copied page images, divider-cell transformations, leaf/non-leaf differences, and parent overflow-cell handling. It intentionally may leave the database corrupt on error with the expectation that the caller rolls back. Tests should treat any new error path in balancing as transaction-rollback-sensitive.

`sqlite3BtreeDeleteRange` returns literal `201` after a successful modified range delete rather than a standard `SQLITE_OK`. Callers must intentionally understand this sentinel. It also has commented-out cursor invalidation and save-all-cursors logic, so concurrent open cursors on the same table may be more fragile than with normal single-row delete.

`sqlite3BtreeLazyDelete` stores page numbers as `int` payloads and reads them through `sqlite3BtreeDataFetch`, expecting exactly `sizeof(int)` bytes. It assumes page numbers fit that representation and that the cursor table is well-formed. Stack overflow is reported as `SQLITE_FULL`.

The open path deliberately ignores the initial header page size. This protects against stale/corrupt headers in WAL/codec scenarios, but it means default page-size and auto-vacuum defaults are used temporarily until page 1 is read through the pager. Code that observes these fields too early would see provisional values.

The partial index comparison optimization depends on `sqlite3VdbeRecordCompare` accurately reporting whether more bytes are required. The `SQLITE3_BTREE_FORCE_FULL_COMPARISONS` debug switch can compare partial and full results, but it is disabled by default.

The chunk ends at the start of `sqlite3BtreeCount`; its full tree-walk implementation and later integrity-check APIs are outside this work item, so count/integrity behavior should be reconciled by the later chunk merge.

## Test Signals

Useful direct tests for this chunk should exercise:

- opening databases with valid page 1 in WAL but misleading initial database-header bytes, especially with pager codecs or checksums;
- shared-cache lock conflicts across read cursors, write cursors, schema table locks, read-uncommitted mode, and exclusive transactions;
- page initialization and corruption detection for malformed headers, invalid cell offsets, overlapping freeblocks, oversized cells, and invalid page flags;
- insert/replace/delete with small local payloads, overflow payloads, integer table keys, index keys, append-biased inserts, root splits, right-edge quick balance, non-root redistribution, and root shallowing;
- cursor stability when other cursors are saved/restored around inserts, deletes, clear-table, rollback, and savepoint rollback;
- freelist allocation/freeing with empty freelists, full trunk pages, exact-page allocation, nearby allocation, truncated leaves, secure delete, and same-transaction free/reuse rollback;
- auto-vacuum relocation, incremental vacuum, full auto-vacuum commit, root-page create/drop movement, and pointer-map updates for b-tree children and overflow pages;
- incremental blob reads/writes and overflow-cache invalidation after row replacement, delete, create table, auto-vacuum, and rollback;
- `sqlite3BtreeLazyDelete` and `sqlite3BtreeDeleteRange` on leaf-only and multi-level trees, including stack exhaustion, pointer-map `PTRMAP_LAZYFREE`, resumed lazy deletion from the cursor table, and the nonstandard `201` return from modified range deletes;
- metadata reads/writes for free-page count, schema cookies, largest root page, and incremental-vacuum flag.

Existing test signals elsewhere in the SQLite suite that should be relevant include btree corruption tests, pager rollback/journal tests, auto-vacuum and incremental-vacuum tests, shared-cache lock tests, overflow payload tests, savepoint tests, and rowid/index cursor movement tests. FoundationDB-specific coverage should add assertions around the modified pointer-map and lazy-delete behavior because upstream SQLite tests will not cover those changes.

### subset-b-008404: lines 7897-8795

# sources/storage-engines/foundationdb/contrib/sqlite/btree.c lines 7897-8795

## Scope And Purpose

This chunk covers the end of SQLite's btree implementation in the FoundationDB-contrib SQLite tree. It starts inside `sqlite3BtreeCount()`, then implements the btree integrity-check machinery, and ends with small public btree accessors and maintenance helpers for filenames, transaction state, WAL checkpointing, schema storage, shared-cache table locks, incremental blob writes, overflow-page caching, and database header format-version changes.

The largest behavioral surface is the integrity checker used by `PRAGMA integrity_check` through `sqlite3BtreeIntegrityCheck()`. It walks freelists, overflow chains, root btrees, and FoundationDB's lazy-delete freetable, marks page references, validates auto-vacuum pointer-map entries, checks rowid ordering for intkey pages, validates overflow ownership, checks child depths, and detects overlapping or missing byte coverage within each btree page.

This span is also where the local FoundationDB fork diverges from stock SQLite semantics. It has a global `g_expect_full_pointermap`, an extended pointer-map type `PTRMAP_LAZYFREE`, a lazy-delete table validator, and a disabled underfull-page check annotated as failing for this fork. Those changes make the integrity check aware of deferred subtree deletion and relaxed page fullness expectations.

## Important APIs, Types, And Functions

`sqlite3BtreeCount(BtCursor *pCur, i64 *pnEntry)` counts entries in the btree addressed by a cursor. The covered portion performs a depth-first page traversal using `moveToRoot()`, `moveToChild()`, and `moveToParent()`. Leaf pages and non-intkey pages contribute `pPage->nCell` to the count. Interior intkey pages do not count interior separator cells as table entries.

`sqlite3BtreePager(Btree *p)` returns the underlying `Pager *` from `p->pBt`. The comment marks it as testing/debug-only, but it is still exported as `SQLITE_PRIVATE`.

`IntegrityCk` is the integrity-check context shared across helper routines. The structure is defined in the btree internals and carries `BtShared *pBt`, `Pager *pPager`, total page count, the `anRef[]` page-reference count array, remaining error budget `mxErr`, accumulated error count `nErr`, `mallocFailed`, and a `StrAccum errMsg`.

`checkAppendMsg()` is the shared error recorder. It decrements the remaining error budget, increments `nErr`, appends an optional context prefix and formatted message to `IntegrityCk.errMsg`, and propagates `StrAccum` allocation failure into `IntegrityCk.mallocFailed`.

`checkRef()` validates a page number and increments `anRef[iPage]`. It reports out-of-range page numbers and a second reference to the same page, returning nonzero when the page is invalid or already referenced.

`checkPtrmap()` is compiled when auto-vacuum support is present. It reads a pointer-map entry with `ptrmapGet()` and checks that the child page maps to the expected pointer-map type and parent page. This chunk uses stock pointer-map categories like `PTRMAP_BTREE`, `PTRMAP_ROOTPAGE`, `PTRMAP_OVERFLOW1`, `PTRMAP_OVERFLOW2`, `PTRMAP_FREEPAGE`, and `PTRMAP_FREELEAF`, plus this fork's `PTRMAP_LAZYFREE`.

`checkList()` validates either the main freelist or an overflow-page chain. For freelists, each trunk page is read through the pager, its leaf count is range checked against usable page size, free leaves are marked in `anRef[]`, and pointer-map entries are optionally checked when `pBt->autoVacuum && g_expect_full_pointermap`. For overflow lists, it verifies chained overflow pointer-map ownership and uses the expected page count to detect missing or extra list pages.

`checkTreePage()` recursively validates one btree page and its descendants. It loads and initializes the page, checks cell payloads and overflow chains, validates intkey rowid ordering within a page and against parent bounds, verifies auto-vacuum pointer-map ownership for child pages and overflow roots, checks equal child depth, optionally prints a verbose tree view, and then builds a byte-hit map to ensure cells, freeblocks, header/cell-pointer area, content area, and fragmented bytes account for the page without overlap.

`checkLazyDeleteTable()` is a FoundationDB-specific integrity extension. It opens a read cursor on the lazy-delete table root, iterates each intkey record, reads an `int` page number from the record payload, checks that the page has pointer-map type `PTRMAP_LAZYFREE`, and runs `checkTreePage()` on that lazily deleted subtree.

`sqlite3BtreeIntegrityCheck(Btree *p, int *aRoot, int nRoot, int mxErr, int *pnErr, int verbose)` is the exported integrity-check entry point. It initializes `IntegrityCk`, allocates and zeroes `anRef[]`, reserves the pending-byte page as referenced, validates the freelist, checks each root in `aRoot[]`, checks the lazy-delete freetable at `aRoot[nRoot - 1]`, reports unreferenced pages and referenced pointer-map pages, verifies pager refcount stability, and returns either a malloc-owned error string or `NULL`.

The remaining exported helpers are narrower:

- `sqlite3BtreeGetFilename()` and `sqlite3BtreeGetJournalname()` return pager file and journal paths.
- `sqlite3BtreeIsInTrans()`, `sqlite3BtreeIsInReadTrans()`, and `sqlite3BtreeIsInBackup()` expose write/read transaction and backup state.
- `sqlite3BtreeCheckpoint()` gates WAL checkpoints on there being no active shared-btree transaction, then delegates to `sqlite3PagerCheckpoint()`.
- `sqlite3BtreeSchema()` lazily allocates per-`BtShared` schema memory and stores its destructor.
- `sqlite3BtreeSchemaLocked()` checks for a shared-cache read lock conflict on `MASTER_ROOT`.
- `sqlite3BtreeLockTable()` takes a shared-cache read or write table lock when the btree handle is sharable.
- `sqlite3BtreePutData()` writes into an existing intkey row payload for incremental blob handles without changing payload length.
- `sqlite3BtreeCacheOverflow()` marks a cursor as an incremental blob handle and invalidates any old overflow-page cache.
- `sqlite3BtreeSetVersion()` updates database header bytes 18 and 19 to read/write version 1 or 2, using a two-phase transaction escalation if the header actually needs modification.

## Control Flow

The `sqlite3BtreeCount()` traversal is an explicit depth-first walk over btree pages. Starting from the root, it counts entries on countable pages, backs up from leaves until it finds an unvisited parent branch, advances the parent index, and descends either through a cell's left-child page number or the right-child pointer at `hdrOffset + 8`. Completion is detected when the traversal backs up from a leaf to the root with no remaining branches.

The integrity-check entry flow begins in `sqlite3BtreeIntegrityCheck()`. It enters the btree mutex, asserts that at least a read transaction is open, snapshots the pager reference count, derives the current database page count, and returns immediately for an empty database. It then allocates `anRef[]`, initializes the error accumulator with a small stack buffer and heap growth limit, marks the pending-byte page, and starts structural checks.

Freelist checking goes through `checkList(isFreeList=1, firstTrunk, totalFreePages, "Main freelist: ")`. Each trunk page is marked, read, and parsed. The first 4 bytes link to the next trunk and the next 4 bytes hold the number of free leaf page numbers stored in the trunk. The routine decrements the expected remaining page count for both trunk and valid leaf entries, reports too many leaves for the usable page size, and reports missing, extra, or excessive pages after the traversal.

Root btree checking loops over `aRoot[0..nRoot-1]`. Root page 0 is skipped. Under auto-vacuum, non-page-1 roots are checked as `PTRMAP_ROOTPAGE`. `checkTreePage()` then recursively descends through each interior cell's child pointer and finally the right-child pointer. For each cell it parses payload metadata with `btreeParseCellPtr()`, checks local versus overflow payload size, verifies the first overflow page pointer when the payload spills, recursively checks the overflow chain through `checkList(isFreeList=0, ...)`, and recurses into child pages for non-leaf nodes.

The byte-coverage portion of `checkTreePage()` allocates a `hit` array with one byte per database-page byte. It marks the header/cell-pointer area and the unused space before the content area, then increments the hit count over each cell body and each freeblock. Any zero hit indicates a byte not covered by known page regions; multiple hits indicate overlapping use. The zero-hit count must match the page header's fragmentation byte count. This catches page-local corruption independently of cross-page reference checks.

After ordinary roots, `sqlite3BtreeIntegrityCheck()` calls `checkLazyDeleteTable()` using the last root entry as the lazy-delete freetable. This helper opens a cursor with `sqlite3BtreeCursor()`, seeks to the first entry, and iterates with `sqlite3BtreeNext()`. For each record, `sqlite3BtreeKeySize()` retrieves the intkey rowid, `sqlite3BtreeDataFetch()` returns the stored page number, and the page is checked both as a lazy-free pointer-map entry and as a btree subtree.

The final integrity pass scans all page numbers from 1 to `nPage`. Without auto-vacuum, any unreferenced page is an error. With auto-vacuum, unreferenced pointer-map pages are allowed, but unreferenced ordinary pages are reported along with pointer-map metadata if readable, and referenced pointer-map pages are reported as corruption. Before returning, the function compares the pager refcount to the saved value to catch leaks in the checker itself, leaves the btree mutex, frees `anRef[]`, and finalizes or resets the accumulated error text.

The late utility functions are mostly direct wrappers. They enter the btree mutex only when reading mutable shared-btree state or invoking pager/shared-cache operations. `sqlite3BtreePutData()` first restores the cursor position, validates writable incremental-blob preconditions, then delegates to `accessPayload()` with the write flag. `sqlite3BtreeSetVersion()` opens a read transaction first, temporarily suppresses automatic WAL use when forcing version 1, escalates to a write transaction only if bytes 18 or 19 differ, writes page 1 through the pager, updates the header bytes, and clears `doNotUseWAL`.

## State And Persistence Behavior

The integrity checker is read-oriented but stateful. Its durable inputs are database pages, page-1 metadata, btree page headers, overflow chains, freelist trunks, auto-vacuum pointer-map pages, and lazy-delete records. Its in-memory state is `IntegrityCk`, especially `anRef[]`, which tracks whether each database page has been seen and detects duplicate ownership.

`checkTreePage()` deliberately clears `MemPage.isInit` before calling `btreeInitPage()` so that page-format corruption checks run even if the page had already been initialized in cache. It releases every `MemPage` or `DbPage` it acquires through `releasePage()` or `sqlite3PagerUnref()`, and the outer integrity check verifies that pager reference counts return to their entry value.

The checker mutates only diagnostic state during normal operation: `mxErr`, `nErr`, `mallocFailed`, and the accumulated string. It may also alter cached page initialization flags, but it does not call pager-write APIs and does not persist page changes.

`sqlite3BtreeSchema()` persists schema-side state for the lifetime of `BtShared`, not to disk. The first nonzero allocation request creates zeroed memory stored in `pBt->pSchema` and records `pBt->xFreeSchema`; later calls return the same pointer and ignore `nBytes`.

`sqlite3BtreePutData()` is durable mutation. It writes a byte range into the existing payload of the row under an incremental blob cursor. It depends on an active write transaction, a valid intkey-table row, no conflicting read locks, and `accessPayload()` to route writes through local cell payload or overflow pages. It cannot resize the row; attempts beyond the stored payload are expected to fail through the payload-access path.

`sqlite3BtreeSetVersion()` is also durable mutation. It writes database header fields for read and write file-format versions. The `doNotUseWAL` flag is a transient guard so that forcing version 1 does not automatically open WAL because the current header still says version 2.

WAL checkpointing persists pager/WAL state but not btree pages directly. `sqlite3BtreeCheckpoint()` refuses to checkpoint while the shared btree has an active transaction and otherwise delegates to the pager.

## Dependencies And Integration Points

This chunk is tightly integrated with btree cursor navigation (`moveToRoot`, `moveToChild`, `moveToParent`, `findCell`, `cellSizePtr`, `btreeParseCellPtr`), page lifecycle helpers (`btreeGetPage`, `getAndInitPage`, `btreeInitPage`, `releasePage`), overflow cleanup/list logic (`clearCell`, `checkList`), big-endian page-field helpers (`get2byte`, `get2byteNotZero`, `get4byte`), and pager APIs (`sqlite3PagerGet`, `sqlite3PagerGetData`, `sqlite3PagerUnref`, `sqlite3PagerRefcount`, `sqlite3PagerFilename`, `sqlite3PagerJournalname`, `sqlite3PagerCheckpoint`, `sqlite3PagerWrite`).

The integrity entry point is used by the VDBE `OP_IntegrityCk` path generated for `PRAGMA integrity_check` and `PRAGMA quick_check`. The SQL layer supplies the root-page array and error budget; this function returns a newline-separated message string and writes the number of reported errors to `pnErr`.

Auto-vacuum integration depends on pointer-map primitives (`ptrmapGet`, `ptrmapPut` elsewhere) and pointer-map page-number calculations through `PTRMAP_PAGENO()`. The FoundationDB lazy-delete extension integrates with `sqlite3BtreeLazyDelete()` from the preceding chunk: that code stores lazily deleted subtree roots in a table and marks them `PTRMAP_LAZYFREE`; this chunk validates those records and subtrees.

Shared-cache integration uses `querySharedCacheTableLock()`, `setSharedCacheTableLock()`, `hasSharedCacheTableLock()`, and `hasReadConflicts()` to enforce schema/table lock rules around schema access, explicit table locks, and incremental blob writes.

The mutex contract is split by API. Integrity checking, schema allocation, schema-lock queries, table locking, checkpointing, and version changes enter the btree mutex or assert the caller holds the database mutex. Filename and journal-name access avoid entering the btree mutex because pager filenames are documented as invariant while the pager is open.

## Risks And Edge Cases

`checkLazyDeleteTable()` assumes the last element of `aRoot[]` is the lazy-delete freetable root. If callers provide ordinary SQLite root arrays without that convention, the checker will open and interpret the wrong table as the lazy-delete table.

`checkLazyDeleteTable()` reads each payload as `sizeof(int)` and casts `sqlite3BtreeDataFetch()` to `int *`. This matches the local `sqlite3BtreeLazyDelete()` writer, but it is endian- and ABI-width-sensitive if database files move across platforms with different integer layout or alignment behavior.

The underfull-page check in `checkTreePage()` is commented out with a note that it fails for this fork. That suppresses a traditional btree balance invariant and makes integrity-check success less strict about space utilization. It may be intentional for lazy deletion or FoundationDB behavior, but it narrows what `integrity_check` can prove.

Pointer-map validation for freelist pages is conditional on both auto-vacuum and `g_expect_full_pointermap`. When the global is false, the checker skips some freelist pointer-map expectations even in auto-vacuum databases. Tests need to cover both modes because corruption can be hidden in the default mode.

The rowid ordering checks only apply to intkey pages, and the detailed parent-bound propagation is strongest for intkey leaf pages. Non-intkey index key ordering is explicitly listed as not checked in the function comment.

The recursive `checkTreePage()` walk can be expensive on large databases and consumes C stack proportional to tree depth. SQLite btrees are shallow under normal page sizes, but corrupted child cycles are guarded mainly by `checkRef()` duplicate detection and the error budget.

`checkList()` continues to parse freelist leaf entries only if the free page number is `<= nPage`; it does not emit a direct error for an out-of-range free leaf in that inner loop. Trunk page bounds and duplicate checks are stricter.

`sqlite3BtreePutData()` relies on asserts for several write-transaction and locking invariants, while only `wrFlag`, restored cursor state, and valid cursor state are runtime-checked. Misuse in non-assert builds can become corruption risk if callers violate the expected btree-layer contract.

`sqlite3BtreeSetVersion()` asserts there is no active transaction before it starts. It temporarily sets `pBt->doNotUseWAL`; any early return path must clear it. This implementation clears it after the transaction attempts, but future edits should preserve that cleanup.

## Test Signals

The primary end-to-end signal is `PRAGMA integrity_check` or the VDBE `OP_IntegrityCk` path on databases with normal tables, indexes, overflow payloads, freelist pages, auto-vacuum pointer maps, WAL mode, and FoundationDB lazy-delete state.

Focused corruption tests should exercise duplicate page references, invalid page numbers, malformed freelist trunk leaf counts, missing and extra overflow pages, incorrect `PTRMAP_OVERFLOW1` and `PTRMAP_OVERFLOW2` entries, incorrect root and btree child pointer-map entries, referenced pointer-map pages, unreferenced ordinary pages, and page byte-overlap or fragmentation mismatches.

FoundationDB-specific tests should create lazy-delete table records through `sqlite3BtreeLazyDelete()`, then verify that integrity check accepts `PTRMAP_LAZYFREE` subtrees and rejects records whose payload is not exactly `sizeof(int)`, whose page is not marked `PTRMAP_LAZYFREE`, or whose lazily deleted subtree is structurally corrupt.

Incremental blob tests should validate `sqlite3BtreePutData()` on local payload and overflow payload rows, including writes at the end boundary, writes past the end returning an error without mutation, non-writable cursors returning `SQLITE_READONLY`, invalid cursor state returning `SQLITE_ABORT`, and overflow-cache invalidation through `sqlite3BtreeCacheOverflow()`.

Version and WAL tests should verify that `sqlite3BtreeSetVersion()` updates header bytes 18 and 19 only inside a write transaction, does not leave `doNotUseWAL` set, and interacts correctly with checkpoint refusal in `sqlite3BtreeCheckpoint()` when a transaction is active.
