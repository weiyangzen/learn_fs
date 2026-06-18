<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_btree.c -->
# sources/storage-engines/sqlite/src/test_btree.c

## Purpose
`test_btree.c` contains small btree debug/test helpers not covered by the larger Tcl btree harness. It reports shared-cache participants and can print active cursor state in debug builds.

## Important APIs, Types, and Functions
`sqlite3BtreeSharedCacheReport()` is a Tcl command-style function that returns pairs of pager filename and `BtShared.nRef`. `sqlite3BtreeCursorList(Btree *p)` prints cursor diagnostics using `sqlite3DebugPrintf()` when `SQLITE_DEBUG` is enabled. It uses `BtShared`, `BtCursor`, `MemPage`, `sqlite3SharedCacheList`, `sqlite3PagerFilename()`, cursor flags, and cursor state.

## Control Flow
The shared-cache report allocates a Tcl list and, when shared cache is not omitted, iterates the global shared-cache list via `GLOBAL(BtShared*, sqlite3SharedCacheList)`. For each shared btree it appends the pager filename and reference count. The cursor-list function walks `p->pBt->pCursor`, reads the current page and index from each cursor, formats root page, read/write mode, current page/index, and EOF state, then prints to debug output.

## State and Persistence Behavior
The file does not mutate btree state. It observes process-global shared-cache structures and live cursor lists. Results are snapshots and may become stale immediately if other code opens/closes shared btrees or cursors.

## Dependencies and Integration Points
It depends on `btreeInt.h`, `tclsqlite.h`, SQLite debug printing, shared-cache internals, and Tcl result construction. It is useful alongside tests that enable shared cache or need internal cursor diagnostics.

## Risks
The helpers read internal global lists without taking explicit locks in this file, so they assume the surrounding test context is serialized or otherwise safe. `sqlite3BtreeCursorList()` is a debug diagnostic and not a stable API. Shared-cache output is absent but still returns Tcl OK when shared cache is omitted.

## Test Signals
Signals are Tcl list pairs for shared-cache filename/reference count and debug log lines for cursor state. Tests can assert that expected databases appear in the shared-cache report and that reference counts change with connection lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_btree.c -->
