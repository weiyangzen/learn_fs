<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_quota.c -->
# sources/storage-engines/sqlite/src/test_quota.c

## Purpose
`test_quota.c` implements the quota VFS shim declared by `test_quota.h`. It tracks groups of database and WAL files by full-path glob pattern, enforces aggregate size limits, invokes callbacks before rejecting growth, and exposes both SQLite VFS and stdio-like APIs for quota-managed files.

## Important APIs, Types, And Functions
Core state lives in `quotaGroup`, `quotaFile`, `quotaConn`, opaque `quota_FILE`, and global `gQuota`. Public APIs include `sqlite3_quota_initialize()`, `sqlite3_quota_shutdown()`, `sqlite3_quota_set()`, `sqlite3_quota_file()`, `sqlite3_quota_fopen()`, `sqlite3_quota_fwrite()`, `sqlite3_quota_ftruncate()`, size/mtime helpers, and `sqlite3_quota_remove()`. VFS wrappers are `quotaOpen()`, `quotaDelete()`, `quotaWrite()`, `quotaTruncate()`, and pass-through wrappers for read, sync, locks, file-control, and shared memory. Tcl commands under `SQLITE_TEST` cover setup, dumps, callbacks, and stdio operations.

## Control Flow
Initialization copies the parent VFS, changes `xOpen` and `xDelete`, enlarges `szOsFile`, and installs version 1 and 2 I/O method tables. Opening a main DB or WAL checks the full name against configured groups; matching files are opened through the parent VFS and linked to a shared `quotaFile`. Writes that extend a tracked file compute the new group total, invoke the group's callback if over limit, and return `SQLITE_FULL` if the limit still blocks growth. File-size and truncate calls resynchronize accounting. Stdio wrappers use the same `quotaFile` records and may shorten writes to avoid crossing a limit.

## State And Persistence Behavior
Quota metadata is entirely in-memory. Persistent effects are the normal database/WAL files and files deleted by quota APIs. `quotaGroup.iSize` is maintained from open/write/truncate/filesize/delete paths but can diverge if external processes modify files; explicit `sqlite3_quota_file()` and true-size helpers reconcile or expose that drift. `deleteOnClose` defers deletion of open files until the last close.

## Dependencies And Integration Points
It depends on SQLite VFS, mutex, allocation, and full-path APIs, plus C stdio, `stat`, `ftruncate`, `fsync`, and Windows UTF-8 to MBCS conversion where applicable. It integrates with testfixture through `Sqlitequota_Init()` and Tcl callbacks that may mutate the quota limit by variable indirection.

## Risks And Test Signals
Risks include non-threadsafe initialize/shutdown, undefined behavior when patterns overlap, accounting drift from outside writers, callback reentrancy or failures, delayed delete semantics, partial stdio writes, and platform-specific path conversion. Test signals include over-limit writes returning `SQLITE_FULL`, callbacks successfully raising limits, DB and WAL sizes counted once across multiple opens, group cleanup after zero limit and close, directory-style `sqlite3_quota_remove()`, stdio short writes, truncation accounting, and Windows path tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_quota.c -->
