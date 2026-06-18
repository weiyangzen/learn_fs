<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test6.c -->
# sources/storage-engines/sqlite/src/test6.c

## Purpose
`test6.c` implements crash and device-simulation support for SQLite tests. It registers a VFS named `crash` that wraps a real VFS, buffers writes in memory, and on sync either flushes, drops, corrupts, truncates, or exits to emulate power failure and device characteristics.

## Important APIs, Types, and Functions
Key types are `WriteBuffer`, `CrashFile`, and global `CrashGlobal g`. `CrashFileVtab` implements SQLite I/O methods version 2, including WAL shared-memory pass-throughs. Tcl commands include `sqlite3_crash_enable`, `sqlite3_crashparams`, `sqlite3_crash_now`, `sqlite3_simulate_device`, `sqlite3_crash_on_write`, `unregister_devsim`, `register_jt_vfs`, and `unregister_jt_vfs`. Core routines are `writeListAppend()`, `writeListSync()`, `cfOpen()`, `cfWrite()`, `cfRead()`, `cfSync()`, and `processDevSymArgs()`.

## Control Flow
When crash VFS is enabled, `cfOpen()` opens the real file via the parent VFS and caches its contents into `CrashFile.zData`. `cfWrite()` updates the cache and appends a write buffer instead of writing through immediately. `cfRead()` reads from the cache. `cfSync()` checks whether the file name matches `g.zCrashFile`, decrements `g.iCrash`, and calls `writeListSync()` with crash mode when the configured sync count reaches zero. `writeListSync()` walks the global write list, choosing actions according to `SQLITE_IOCAP_*` flags and randomness; in crash mode it exits the process after replay/corruption.

## State and Persistence Behavior
All pending writes are held in process-global `g.pWriteList`, ordered across file handles. Non-crash sync flushes relevant buffers, while sequential-device simulation may flush writes before the synced handle. Crash sync may leave writes omitted or garbage sectors written. `cfClose()` flushes pending writes for that handle. `cfFileControl(SQLITE_FCNTL_SIZE_HINT)` can append a truncate-style buffer and extend cached size. Device characteristics and sector size are mutable globals configured by Tcl.

## Dependencies and Integration Points
The file is active only for `SQLITE_TEST` and not `SQLITE_OMIT_DISKIO`. It uses internal VFS wrappers `sqlite3Os*`, Tcl allocation, `sqlite3_randomness()`, SQLite I/O capability flags, external devsym and journal-test VFS registration functions, and the default VFS as parent. WAL shared-memory methods are delegated to the real file handle.

## Risks
The crash path calls `exit(-1)` by design. The global write list is not protected for concurrent use. `CrashFile.zName` stores the VFS `zName` pointer rather than owning a copy. File sizes are narrowed to `int` in cached fields. Random corruption can write whole simulated sectors, so tests must run against disposable files. The VFS models selected device guarantees, not a complete filesystem.

## Test Signals
Signals include process termination at the configured sync, recovery behavior after reopening databases, Tcl errors for bad device options, and visible effects of `atomic`, `safe_append`, `sequential`, and sector-size settings. Tests should reset/unregister simulated VFS layers and avoid sharing crash-global state between cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test6.c -->
