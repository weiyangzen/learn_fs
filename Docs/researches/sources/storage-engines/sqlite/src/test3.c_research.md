<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test3.c -->
# sources/storage-engines/sqlite/src/test3.c

## Purpose
`test3.c` exposes raw btree and cursor operations to Tcl. It targets `btree.c` tests by opening Btree handles outside normal SQL execution, creating cursors, moving them, inserting records, reading pager statistics, and validating varint encode/decode routines.

## Important APIs, Types, and Functions
The central types are `Btree`, `BtCursor`, `BtreePayload`, a fake process-global `sqlite3 sDb`, and reference counter `nRefSqlite3`. Tcl commands include `btree_open`, `btree_close`, `btree_begin_transaction`, `btree_pager_stats`, `btree_cursor`, `btree_close_cursor`, `btree_next`, `btree_eof`, `btree_payload_size`, `btree_first`, `btree_varint_test`, `btree_from_db`, `btree_ismemdb`, `btree_set_cache_size`, and object command `btree_insert`.

## Control Flow
`btree_open()` lazily initializes `sDb` with the default VFS and a recursive mutex, opens a main database btree, sets cache size, and returns a pointer string. `btree_close()` closes the handle and releases the fake connection mutex when the final btree closes. Cursor creation allocates `sqlite3BtreeCursorSize()` bytes with Tcl allocation, locks the table when shared-cache support is present, opens a cursor, then returns its pointer. Cursor operations enter the btree, invoke the relevant internal routine, leave the btree, and convert results to Tcl values. `btree_insert()` builds a `BtreePayload` either for integer-key tables or key-only payloads and calls `sqlite3BtreeInsert()`.

## State and Persistence Behavior
The fake `sqlite3` connection and its mutex are shared by all Btrees opened with this harness. Btree changes persist through the pager backing the opened file after transactions and pager commit behavior are exercised elsewhere. Cursors are manually allocated and must be closed to avoid leaks. `btree_from_db()` returns the main or selected attached database's existing Btree pointer from a live Tcl SQLite handle; subsequent operations must honor the owning database mutex.

## Dependencies and Integration Points
The file depends on `sqliteInt.h`, `btreeInt.h`, `tclsqlite.h`, `sqlite3ErrName()`, pointer conversion helpers, SQLite mutex APIs, pager stats through `sqlite3BtreePager()`, varint helpers `putVarint()`, `getVarint()`, and `getVarint32()`. It integrates with shared-cache tests through `sqlite3BtreeLockTable()` when available.

## Risks
The harness intentionally bypasses SQL-layer validation. It can pass stale or arbitrary pointer strings to internal APIs, leak the fake `sDb` mutex if open/close counts become unbalanced, or close cursors after the owning Btree has gone away. Some cursor movement routines enter the Btree but do not always enter the owning db mutex, unlike stats and creation paths; this reflects historical test assumptions and is risky outside controlled tests.

## Test Signals
Signals include symbolic SQLite error names, pager stats with read/write counters, boolean EOF and memory-db results, payload size, and varint self-test failures with exact mismatch text. Tests should pair opens/closes and cursor allocation/freeing, and should validate both integer-key and index-style insertion paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test3.c -->
