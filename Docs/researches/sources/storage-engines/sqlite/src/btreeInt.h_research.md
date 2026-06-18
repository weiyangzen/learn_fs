# sources/storage-engines/sqlite/src/btreeInt.h

## Purpose

`btreeInt.h` is the private implementation header for SQLite's disk-backed B-tree engine. It documents the database file and page layout, defines in-memory structures derived from on-disk pages, and supplies macros/constants used by `btree.c` and closely related storage code. Compared with `btree.h`, this file is deliberately internal: it exposes `MemPage`, `BtShared`, `BtCursor`, pointer-map constants, page flags, endian helpers, and integrity-check state that must remain tightly synchronized with the implementation.

## Important Types, Structures, and Macros

The leading comment is a compact specification of the SQLite database file format: page numbering starts at 1; page 1 begins with a 100-byte database header; header offsets include page size, file-format read/write versions, reserved bytes, payload fractions, change counter, database size, freelist trunk, freelist count, schema cookie, file format, cache size, largest root page, text encoding, user version, incremental-vacuum mode, application id, version-valid-for, and SQLite version number. It also describes btree page headers, cell pointer arrays, freeblocks, fragments, variable-length integers, cells, overflow pages, and freelist trunk/leaf pages.

`MX_CELL_SIZE(pBt)` and `MX_CELL(pBt)` derive maximum cell and cell-count bounds from `BtShared.pageSize`. The page type flags `PTF_INTKEY`, `PTF_ZERODATA`, `PTF_LEAFDATA`, and `PTF_LEAF` mirror the first byte of each on-disk btree page and drive parser behavior for cells.

`MemPage` stores the decoded state of a pager page: initialization flags, key/layout flags, page number, leaf/interior state, header and cell offsets, local payload limits, free-byte counts, overflow-cell staging arrays, owning `BtShared`, raw page bytes (`aData`, `aDataEnd`, `aCellIdx`, `aDataOfst`), pager handle, and function pointers for cell-size and parse-cell routines. The first eight bytes are special because pager extra storage zeroes only that prefix when a new page is allocated.

`BtLock` records shared-cache table locks by `Btree`, root page, and read/write mode. `Btree` is the per-connection handle with connection pointer, shared `BtShared`, transaction state, sharability/lock flags, incremental-blob and backup counters, data-version cache, shared-cache linked-list fields, debug seek count, and page-1 lock. `BtShared` is the per-database shared state: pager, current db, cursor list, page-1 cache, open flags, auto-vacuum flags, transaction state, payload limits, page size/usable size, transaction count, schema pointer and destructor, mutex, content-tracking bitvec, shared-cache locks/writer state, temp cell buffer, and transfer-row preformat size.

`CellInfo` is the decoded cell contract used by cursor and payload routines: integer key or payload-size value, payload pointer, total payload size, local payload size, and cell size on the btree page. `BtCursor` stores cursor state, flags, pager flags, hints, skip/error code, owning `Btree`/`BtShared`, overflow cache, saved key, linked-list membership, current `CellInfo`, last key, root page, current stack depth, key type, current cell index, parent index stack, `KeyInfo`, current page, and parent page stack. `BTCURSOR_MAX_DEPTH` limits tree depth to 20 and acts as a corruption guard.

Cursor flags include write, valid cached key, valid overflow cache, at-last, incremental blob, multiple cursors on same btree, and pinned states. Cursor states are `CURSOR_VALID`, `CURSOR_INVALID`, `CURSOR_SKIPNEXT`, `CURSOR_REQUIRESEEK`, and `CURSOR_FAULT`, with `skipNext` changing meaning by state. This distinction is important after mutations: a cursor can temporarily retain logical position while physical page references are invalid.

Pointer-map macros and constants (`PTRMAP_PAGENO`, `PTRMAP_PTROFFSET`, `PTRMAP_ISPAGE`, `PTRMAP_ROOTPAGE`, `PTRMAP_FREEPAGE`, `PTRMAP_OVERFLOW1`, `PTRMAP_OVERFLOW2`, `PTRMAP_BTREE`) define auto-vacuum metadata used to find parent pointers when moving pages. `PENDING_BYTE_PAGE(pBt)` reserves the page containing the locking pending byte. `ISAUTOVACUUM(pBt)` collapses auto-vacuum compile-time choices into an expression. `IntegrityCk` collects global state for `PRAGMA integrity_check`, including page references, error accumulator, page counts, heap for cell coverage, and row counts.

## Control Flow and State

The btree implementation loads raw pager pages and initializes `MemPage` structures from on-disk bytes. Page flags decide whether a page has integer keys, data payloads, leaf content, and child pointers. Cursor movement maintains a stack of `MemPage` pointers and cell indexes from root to current page, so seek and next/previous operations can descend, ascend, and rebalance without recomputing from the root each time. Cell parsing produces `CellInfo`, and overflow-page state may be cached in `BtCursor.aOverflow`.

Transactions are represented at two levels: `Btree.inTrans` for the per-connection handle and `BtShared.inTransaction`/`nTransaction`/`pWriter` for shared database state. The `btreeIntegrity(p)` macro asserts that shared transaction state and handle state remain consistent. Shared-cache locking tracks table-root locks through `BtShared.pLock` and uses `BTS_PENDING` and `pWriter` to avoid writer starvation when readers block a writer.

Page free-space state is represented by both raw on-disk freeblock chains and decoded `MemPage.nFree`. Overflow cells staged in `aiOvfl`/`apOvfl` allow page-balancing code to temporarily hold cells before reinserting them into local page layout. `BtShared.pHasContent` records pages moved to the freelist during a transaction so rollback/journaling code can reason about page content.

## Persistence Behavior

This header defines persistent on-disk invariants rather than performing writes itself. The database header offsets, page header fields, cell encoding, overflow chains, freelist trunk layout, and pointer-map format are compatibility-critical. Integer fields are big-endian on disk, and helpers `get2byte`, `put2byte`, `get4byte`, `put4byte`, and `get2byteAligned` centralize access. Any implementation change must preserve file-format compatibility or gate behavior by file-format metadata.

Auto-vacuum persistence is centered on pointer-map pages. Each non-pointer-map database page has at most one parent pointer entry, allowing page moves to update parent references without scanning the entire file. This interacts with root pages, overflow chains, freelist pages, and btree child pages. The largest-root-page metadata in `btree.h` and pointer-map macros here are used together by table/index creation and drop paths in `build.c` and VDBE opcodes.

The database page format also persists payload-locality decisions. `BtShared.maxLocal`, `minLocal`, `maxLeaf`, and `minLeaf` mirror page-size and payload-fraction rules so cells can decide how many bytes remain local versus spill to overflow pages. Corruption defenses depend on `aDataEnd`, `usableSize`, `maskPage`, maximum local payload bounds, and tree-depth checks.

## Dependencies and Integration Points

`btreeInt.h` includes `sqliteInt.h` and uses pager types (`Pager`, `DbPage`), schema/connection types (`sqlite3`, `Schema`), expression accumulator types for integrity checking (`StrAccum`), bitsets (`Bitvec`), key comparison metadata (`KeyInfo`), and core integer typedefs. It is used primarily by the btree implementation, integrity-check code, auto-vacuum page-moving logic, cursor/payload code, and shared-cache locking code.

Its definitions support APIs declared in `btree.h`. `Btree`, `BtShared`, and `BtCursor` are opaque publicly but concrete here. VDBE opcodes generated from `build.c` (`OP_CreateBtree`, `OP_Destroy`, `OP_Clear`, `OP_OpenRead`, `OP_OpenWrite`, `OP_Transaction`) eventually execute against these structures. Schema-builder decisions such as `BTREE_INTKEY` versus `BTREE_BLOBKEY`, auto-vacuum root-page moves, and temp database setup rely on the internal page and pointer-map invariants defined here.

## Risks and Edge Cases

The largest risk is mismatching decoded in-memory assumptions with on-disk bytes. Page header offsets differ for page 1 and leaf/interior pages; cells have optional child pointers, optional data-size varints, integer-key special cases, local/overflow splits, and optional overflow pointers. Corruption or integer overflow in any of those calculations can become a memory safety issue, which explains fields such as `aDataEnd`, depth bounds, and aligned/get helpers.

Shared-cache and transaction fields require strict mutex discipline. Comments specify that `MemPage` is protected by `MemPage.pBt->mutex`, `Btree` fields by `sqlite3.mutex`, and `BtShared` fields mostly by `BtShared.mutex` with exceptions for global shared-list fields. Code that bypasses these rules risks stale cursors, incorrect writer exclusion, or schema-cache races.

Compile-time options reshape the structures and behavior. `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_THREADSAFE`, `SQLITE_OMIT_GENERATED_COLUMNS` consumers, debug builds, and byte-order/compiler macros all affect available fields or helper behavior. Any external assumptions about structure layout are unsafe.

Pointer-map behavior is especially sensitive during page moves and drops. Incorrect parent-type entries can orphan pages or corrupt overflow chains. `PENDING_BYTE_PAGE` must remain unused by normal database allocation to preserve locking behavior.

## Test Signals

Storage tests should cover page sizes from 512 through 65536, page-1 header offsets, leaf and interior btree pages, intkey tables, zerodata/index b-trees, overflow payloads, freelist trunk/leaf handling, and fragment/freeblock accounting. Corruption tests should target malformed varints, bad freeblock chains, bad overflow pointers, impossible tree depth, duplicate page references, pointer-map mismatches, root-page moves, and pending-byte-page allocation attempts.

Concurrency and shared-cache tests should verify read/write table locks, pending writer behavior, cursor fault propagation, cursor restore after mutation, pinned cursors, and incremental blob cursor interactions. Auto-vacuum tests should create/drop tables and indexes while verifying pointer-map entries, root-page movement, freelist counts, and schema rootpage updates. Integrity-check tests should assert that `IntegrityCk` catches duplicate use, orphaned pages, and malformed btree coverage.
