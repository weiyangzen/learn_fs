# sources/storage-engines/sqlite/src/os.h

Purpose: declares SQLite's internal OS abstraction layer and common file-locking constants. It is included by `sqliteInt.h`, making its definitions widely visible across the core.

Important declarations and macros: includes `os_setup.h`, supplies defaults for `SET_FULLSYNC`, `SQLITE_MAX_PATHLEN`, `SQLITE_MAX_SYMLINK`, `SQLITE_DEFAULT_SECTOR_SIZE`, and `SQLITE_TEMP_FILE_PREFIX`. Defines lock levels `NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`; lock-byte layout `PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, and `SHARED_SIZE`; and declares all `sqlite3Os*` file/VFS wrapper functions. It also declares `SQLITE_FCNTL_DB_UNCHANGED`.

Control flow: no runtime code. The header establishes contracts consumed by pager, btree, WAL, and VFS code. The lock-byte comments define cross-platform file-locking semantics used by Unix and Windows backends.

State and persistence: no state. `PENDING_BYTE` may be fixed or refer to `sqlite3PendingByte` depending on `SQLITE_OMIT_WSD`, affecting where lock bytes reside in database files.

Dependencies and integration points: depends on standard `FILENAME_MAX`, SQLite integer typedefs, `sqlite3_file`, `sqlite3_vfs`, and compile-time OS selection from `os_setup.h`. The lock constants are integral to database file format compatibility because the pager avoids allocating lock-byte pages.

Risks: changing `PENDING_BYTE` or related byte ranges can create subtle database compatibility changes. Defaults like sector size and temp prefix affect platform behavior and tests. The declarations must match `os.c`; mismatches would surface as build or ABI issues.

Test signals: compile all VFS backends against the header; run locking tests on Unix/Windows; run tests with low `PENDING_BYTE`; verify temp-file behavior with default and overridden prefix; and build with `SQLITE_OMIT_WAL` / mmap variations to check conditional declarations.
