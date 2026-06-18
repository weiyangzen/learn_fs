# sources/storage-engines/wiredtiger/examples/c/ex_file_system.c

Purpose: implements an in-memory custom `WT_FILE_SYSTEM`/`WT_FILE_HANDLE` extension and uses it to back a WiredTiger table.

Important APIs and control flow: `DEMO_FILE_SYSTEM` embeds `WT_FILE_SYSTEM` first, stores a global rwlock, counters, handle queue, and extension API. `DEMO_FILE_HANDLE` embeds `WT_FILE_HANDLE` first, tracks owning FS, queue node, refcount, buffer, buffer capacity, and logical size. `demo_file_system_create` parses custom extension config, initializes callback tables, and calls `conn->set_file_system`. Filesystem callbacks implement open, directory listing/free, existence, remove, rename, size, and termination. File callbacks implement close, lock, read, size, sync, truncate, and write. `main` loads the local extension with `early_load=true`, creates `table:fs`, inserts 1000 rows, rescans and verifies ordered keys, then closes.

State and persistence: file contents live only in heap buffers for the connection lifetime. Counters are printed at termination. A WT_HOME directory is created only as an anchor; storage is redirected through the custom FS.

Dependencies and integration: requires POSIX pthread rwlocks, TAILQ macros from included test/util headers, local extension symbol visibility, early extension loading, and WiredTiger file-system ABI.

Risks: a single global write lock serializes all I/O and schema activity. The directory prefix check compares prefix against the full name, which is simplistic. `memset(entries + allocated * sizeof(*entries), ...)` uses pointer arithmetic incorrectly for an array of pointers. The implementation supports only one open reference per file.

Test signals: insertion/rescan of 1000 ordered keys validates basic read/write/size/open behavior, and termination counters show file lifecycle coverage.
