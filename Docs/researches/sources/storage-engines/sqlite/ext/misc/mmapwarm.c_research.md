# sources/storage-engines/sqlite/ext/misc/mmapwarm.c

Purpose: implements `sqlite3_mmap_warm()`, a C helper that touches mapped database pages so the OS caches them.

Important APIs/types/functions: the exported `sqlite3_mmap_warm(sqlite3*, const char*)` uses `sqlite3_get_autocommit()`, dynamic SQL over `sqlite_schema`, `PRAGMA page_size`, `SQLITE_FCNTL_FILE_POINTER`, and VFS `xFetch()`/`xUnfetch()`.

Control flow: rejects active transactions with `SQLITE_MISUSE`, opens a read transaction, reads page size, obtains the `sqlite3_file`, then loops over mapped page offsets, touching first and last bytes before unfetching. It logs warmed page count and ends the transaction.

State and persistence: no database writes; temporary read transaction and OS cache effects only.

Dependencies/integration: SQLite C/VFS APIs and mmap-capable VFS method version 3 or newer.

Risks/test signals: transaction cleanup on failure, attached-schema quoting, partial mappings, VFS-specific fetch semantics, and non-mmap no-op behavior. Test main/attached DBs, calls inside transactions, VFS without mmap, page-size failure, and complete `END` cleanup.
