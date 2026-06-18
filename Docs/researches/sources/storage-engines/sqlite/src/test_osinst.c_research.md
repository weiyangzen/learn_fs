<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_osinst.c -->
# sources/storage-engines/sqlite/src/test_osinst.c

## Purpose
`test_osinst.c` implements a VFS instrumentation wrapper plus a `vfslog` virtual table for reading the generated binary logs. It is test-only infrastructure for measuring and inspecting SQLite VFS and file-method calls with low logging overhead.

## Important APIs, Types, And Functions
Key objects are `VfslogVfs`, which wraps a parent `sqlite3_vfs` and owns a buffered log file, and `VfslogFile`, which wraps each underlying `sqlite3_file`. Public C entry points are `sqlite3_vfslog_new()`, `sqlite3_vfslog_finalize()`, `sqlite3_vfslog_annotate()`, and `sqlite3_vfslog_register()`. Wrapped methods include `vfslogOpen()`, `vfslogRead()`, `vfslogWrite()`, `vfslogSync()`, lock/unlock, and shared-memory methods. The virtual table side uses `VfslogVtab`, `VfslogCsr`, `vlogConnect()`, `vlogNext()`, and `vlogColumn()`.

## Control Flow
`sqlite3_vfslog_new()` finds the parent VFS, allocates a larger VFS object that includes the parent file storage for the log, opens a fresh log file, writes a magic header, and registers the wrapper as default. Each wrapped VFS or file method measures elapsed time, calls the real method, then appends a 24-byte big-endian record. Events carrying a path or annotation append a length-prefixed string. The virtual table opens a log file, skips the 20-byte header, decodes records sequentially, tracks file ids from `xOpen`, and exposes event name, filename, click count, return code, size, and offset columns.

## State And Persistence Behavior
The wrapper persists binary records to the configured log file through an 8 KB in-memory buffer. It stores per-wrapper counters, log offset, and next file id. Reader cursors maintain transient file-id-to-name mappings while scanning. In test builds, `vfslog_flush()` temporarily disables SQLite's simulated I/O and disk-full faults to avoid recursive corruption of the instrumentation log.

## Dependencies And Integration Points
It depends on SQLite VFS version 2 file methods for shared-memory logging, Tcl testfixture bindings under `SQLITE_TEST` or `TCLSH`, and virtual-table support for log reading. The Tcl command `vfslog` exposes `new`, `finalize`, `annotate`, and `register`.

## Risks And Test Signals
Risks include truncated timing to 16 bits, integer truncation of 64-bit offsets and sizes, missing logging for `xFileControl` and most VFS utility methods, assumptions about record framing, and limited validation of malformed log files. Test signals include successful wrapper creation/finalization, readable `vfslog` rows matching known SQLite operations, path association through `xOpen`, annotation records, WAL shared-memory event capture, and clean behavior under injected I/O faults.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_osinst.c -->
