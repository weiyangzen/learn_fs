<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_delete.c -->
# sources/storage-engines/sqlite/src/test_delete.c

## Purpose
`test_delete.c` implements `sqlite3_delete_database()`, a test utility that removes an SQLite database and associated sidecar files, including journal, WAL, shared-memory, 8.3-name variants, and multiplexor chunk files.

## Important APIs, Types, and Functions
The public function is `sqlite3_delete_database(const char *zFile)`. Helpers are `sqlite3Delete83Name()` and `sqlite3DeleteUnlinkIfExists()`. It uses SQLite allocation and formatting APIs, POSIX `access()` and `unlink()` on non-Windows, and the `win32` VFS `xDelete()` on Windows. It copies multiplex constants `MX_CHUNK_NUMBER`, `SQLITE_MULTIPLEX_JOURNAL_8_3_OFFSET`, and `SQLITE_MULTIPLEX_WAL_8_3_OFFSET`.

## Control Flow
The function allocates a filename buffer sized from the input path. It first deletes base files generated from `%s`, `%s-journal`, `%s-wal`, and `%s-shm`, and for sidecars also tries the 8.3-transformed name. It then scans multiplex chunk patterns for database, journal, and WAL chunks, both normal and 8.3 forms, stopping each sequence when a chunk no longer exists or an error occurs. Any system/VFS error maps to `SQLITE_ERROR`, while allocation failure returns `SQLITE_NOMEM`.

## State and Persistence Behavior
This function destructively deletes files from the filesystem. It assumes `zFile` is a plain filename, not a URI. It does not coordinate with live SQLite connections or locks; callers must ensure the database is not in use.

## Dependencies and Integration Points
It integrates with test code that needs a stronger cleanup primitive than deleting only the main database file. On Windows it routes through the SQLite VFS to match platform delete behavior; on POSIX it uses direct filesystem calls and asserts no VFS pointer is used.

## Risks
The function is destructive and broad: multiplex scans can remove many numbered files derived from the input name. It collapses most OS errors to `SQLITE_ERROR`, losing diagnostics. It has no locking or safety checks for open databases. `sqlite3Delete83Name()` intentionally mimics internal 8.3 suffix logic, so any divergence from SQLite's filename algorithm could leave files behind or target the wrong transformed path.

## Test Signals
Signals include `SQLITE_OK`, `SQLITE_NOMEM`, or `SQLITE_ERROR`, and the absence of main, journal, WAL, SHM, 8.3, and multiplex files after cleanup. Tests should use disposable paths and verify no live connection holds the target database.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_delete.c -->
