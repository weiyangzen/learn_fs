<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_quota.h -->
# sources/storage-engines/sqlite/src/test_quota.h

## Purpose
`test_quota.h` declares the public interface for SQLite's test quota VFS shim. It documents the quota model: files are grouped by full-path glob, group size is capped by a configurable limit, and a callback can raise the limit before writes fail.

## Important APIs, Types, And Functions
The header exposes lifecycle APIs `sqlite3_quota_initialize()` and `sqlite3_quota_shutdown()`, group configuration through `sqlite3_quota_set()`, and file enrollment through `sqlite3_quota_file()`. It defines opaque `quota_FILE` and declares stdio-like wrappers: `sqlite3_quota_fopen()`, `sqlite3_quota_fread()`, `sqlite3_quota_fwrite()`, `sqlite3_quota_fflush()`, `sqlite3_quota_fclose()`, `sqlite3_quota_fseek()`, `sqlite3_quota_rewind()`, `sqlite3_quota_ftell()`, `sqlite3_quota_ferror()`, `sqlite3_quota_ftruncate()`, `sqlite3_quota_file_mtime()`, size/truesize/available helpers, and `sqlite3_quota_remove()`.

## Control Flow
Callers initialize the shim once, define one or more distinct quota groups before opening participating database connections, then operate normally through the `quota` VFS or the `quota_FILE` APIs. When a write would extend a file past the group limit, the callback receives the filename, an in/out limit pointer, proposed total size, and client data. Shutdown requires all SQLite connections to be closed.

## State And Persistence Behavior
The header owns no state, but its contract describes in-memory quota accounting layered over persistent files. It explicitly warns that the quota-known size may differ from the true on-disk size if external modification or unflushed stdio writes occur.

## Dependencies And Integration Points
It includes `sqlite3.h`, stdio, and stat/time-related system headers, and is C++ friendly via `extern "C"`. `test_quota.c` implements the declarations and Tcl test bindings use the same API surface.

## Risks And Test Signals
Risks include misuse of initialize/shutdown ordering, overlapping glob patterns, callers assuming UTF-8 globbing is character-aware rather than byte-based, and using truncate to extend a quota-managed file despite documented undefined behavior. Test signals include API compile coverage from C and C++, callback limit mutation, unmanaged-file no-ops, true-size versus quota-size checks, and removal of managed files and managed directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_quota.h -->
