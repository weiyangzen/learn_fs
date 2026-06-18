<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test2.c -->
# sources/storage-engines/sqlite/src/test2.c

## Purpose
`test2.c` exposes low-level pager and fault-injection internals to the Tcl test harness. It is not part of the SQLite library; it lets scripts open raw `Pager` handles, fetch and mutate `DbPage` objects, control savepoint-style pager checkpoints, synthesize sparse files, and install test-control callbacks.

## Important APIs, Types, and Functions
The file registers Tcl commands in `Sqlitetest2_Init()`: `pager_open`, `pager_close`, `pager_commit`, `pager_rollback`, `pager_stmt_begin`, `pager_stmt_commit`, `pager_stmt_rollback`, `pager_stats`, `pager_pagecount`, `page_get`, `page_lookup`, `page_unref`, `page_read`, `page_write`, `page_number`, `pager_truncate`, optional `fake_big_file`, `sqlite3BitvecBuiltinTest`, `sqlite3_test_control_pending_byte`, and `sqlite3_test_control_fault_install`. It uses `Pager`, `DbPage`, `sqlite3PagerOpen()`, `sqlite3PagerGet()`, `sqlite3PagerWrite()`, `sqlite3PagerCommitPhaseOne/Two()`, `sqlite3PagerSavepoint()`, `sqlite3PagerStats()`, and `sqlite3_test_control()`. `test_pagesize` is a process-global pager size used by `pager_open()` and `page_write()`.

## Control Flow
`pager_open()` builds a read-write main-db pager over the default VFS, sets cache size and page size, then returns a pointer string. Page commands convert pointer strings back to native pointers with `sqlite3TestTextToPtr()`. `page_get()` first obtains a shared lock, then loads the requested page. `page_write()` marks the page writable before copying Tcl text into the page buffer. Statement commands map to one savepoint slot: open savepoint 1, rollback/release savepoint 0, or release savepoint 0. Commit performs phase one followed by phase two and returns Tcl errors on either failure.

## State and Persistence Behavior
Pager state is real database state. `page_write()` changes cached page content and persistence occurs only after commit and sync behavior in the pager. `pager_truncate()` truncates the pager image, not necessarily the on-disk file immediately. `fake_big_file()` writes at an `N` megabyte offset to create sparse storage conditions. Fault simulation stores global `faultSimInterp`, `faultSimScriptSize`, and `faultSimScript`; once installed, `sqlite3FaultSim()` calls evaluate Tcl script text with an appended integer argument.

## Dependencies and Integration Points
This file depends on internal SQLite headers `sqliteInt.h`, `tclsqlite.h`, pager internals, default VFS functions, Tcl command registration, external `sqlite3ErrName()`, and test globals for I/O and disk-full simulation. It links Tcl variables such as `sqlite_io_error_pending`, `sqlite_diskfull`, and read-only `sqlite_pending_byte`, allowing existing Tcl test scripts to observe and manipulate error simulation.

## Risks
Pointer strings expose raw `Pager` and `DbPage` addresses with no lifetime validation. Misordered Tcl calls can use pages after unref or pagers after close. `page_read()` copies 100 bytes into a stack buffer and returns it as a string, so embedded zero bytes truncate Tcl string semantics. `faultSimCallback()` mutates a shared script buffer and interpreter globals, so it is not isolated across concurrent tests. `fake_big_file()` can create very large sparse files and is disabled only for diskless builds; Windows restricts the requested size.

## Test Signals
Useful signals include pager statistics names and counters, pager page count, returned SQLite symbolic error names, linked I/O error counters, bitvec test-control return codes, and callback-driven fault results. Tests should assert correct error propagation for lock/get/write/commit paths and reset fault-control state after use.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test2.c -->
