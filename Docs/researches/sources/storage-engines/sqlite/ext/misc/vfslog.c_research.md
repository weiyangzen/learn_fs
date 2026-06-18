# Research: sources/storage-engines/sqlite/ext/misc/vfslog.c

## Purpose

`vfslog.c` implements an SQLite VFS wrapper named `vfslog` that logs disk activity for main database files and rollback journals. It is intended for debugging and I/O analysis rather than normal application use. The wrapper delegates all real filesystem work to the process default VFS, but records CSV rows containing timestamps, elapsed time, operation name, target class, arguments, signatures of read/write buffers, and result codes.

The file is designed for embedding into the SQLite amalgamation with `SQLITE_EXTRA_INIT=sqlite3_register_vfslog` and optionally `SQLITE_USE_FCNTL_TRACE`. When registered, it becomes the default VFS and records one log file per database connection/database path, avoiding concurrent-process writes to a single shared log.

## Important APIs, Types, And Functions

- `sqlite3_register_vfslog(const char *zArg)` installs the wrapper around `sqlite3_vfs_find(0)`, sets `szOsFile` to include `VLogFile` plus the real VFS file object, and registers `vfslog` as default.
- `VLogVfs` embeds `sqlite3_vfs` and stores `pVfs`, the parent VFS.
- `VLogFile` embeds `sqlite3_file`, points to the real file object stored inline after itself, and references the relevant `VLogLog`.
- `VLogLog` tracks a shared log stream, reference count, canonical database filename length, optional filename, and list links. A paired `VLogLog[2]` allocation represents the main database and its rollback journal, with the journal entry using `zFilename==NULL` but sharing `out`.
- `vlogLogOpen()` canonicalizes journal/main database association, skips WAL and master-journal files, creates a unique `*-debuglog-<timestamp>` file, links it into `allLogs`, and emits an `IDENT` row on Unix.
- `vlogLogPrint()` formats CSV rows and uses SQLite `%w` escaping for string arguments.
- File methods `vlogRead`, `vlogWrite`, `vlogSync`, `vlogLock`, `vlogUnlock`, `vlogFileControl`, and companions time and log calls before/after delegating to `pReal->pMethods`.
- `vlogSignature()` records a full hex dump for buffers up to 16 bytes, or first-eight-bytes plus a simple 64-bit-style checksum for larger buffers.
- `bigToNative()` and the change-counter logic in `vlogRead`/`vlogWrite` add `CHNGCTR-READ` and `CHNGCTR-WRITE` rows when page-1 header bytes 24..39 are touched.

## Control Flow

Registration captures the current default VFS and publishes a wrapper VFS with version 1 I/O methods. On `xOpen`, `vlogOpen` stores the real `sqlite3_file` immediately after `VLogFile`, opens or reuses a log for main DB or main journal files, delegates to the real VFS, logs `OPEN`, and installs `vlog_io_methods` only on success. Non-main files are opened without a log pointer.

For each file call, the wrapper records `vlog_time()` before delegating, calls the real method, computes elapsed time, and writes a CSV row if a log is available. Reads and writes additionally compute a content signature, and successful accesses overlapping the SQLite database header change-counter region emit semantic change-counter rows. Most VFS-level methods (`xDelete`, `xAccess`) temporarily open a log by path, log the call, then decrement the reference.

Closing a wrapped file delegates `xClose`, logs `CLOSE`, and calls `vlogLogClose`. The log object is refcounted; the main log entry owns the list node, `FILE *`, and allocation, while the journal pair element just decrements and returns.

## State And Persistence Behavior

The persistent side effect is a CSV log file adjacent to or named from the database path: `"<db>-debuglog-<microsecond timestamp>"`. It is opened append-mode and flushed only by stdio behavior, not explicitly after every row. Each log file contains rows for one SQLite connection's main database and rollback journal traffic. WAL files and master journals are deliberately not logged.

Process-local state is held in `allLogs`, protected by `SQLITE_MUTEX_STATIC_MASTER` only while searching/linking/unlinking log objects. Reference increments happen after the mutex is released, so the code assumes SQLite's open/close sequencing and shared log reuse are sufficient for this diagnostic extension. Timing uses microseconds from `gettimeofday` on Unix, `GetSystemTimeAsFileTime` on Windows, and zero elsewhere.

## Dependencies And Integration Points

This code depends on SQLite's VFS and I/O method ABI, SQLite memory and formatting helpers, `SQLITE_FCNTL_TRACE`, `SQLITE_FCNTL_PRAGMA`, `SQLITE_FCNTL_SIZE_HINT`, and platform time/identity APIs. It integrates by becoming the default VFS, so all later SQLite connections use it unless a different VFS is chosen. It wraps `xFileControl(SQLITE_FCNTL_VFSNAME)` to prepend `vlog/` to the underlying VFS name.

## Risks And Edge Cases

- The wrapper advertises I/O method version 1 and leaves shared-memory and mmap methods NULL, so WAL-mode behavior is intentionally not instrumented and may be unavailable through this VFS depending on SQLite expectations.
- `vlogSignature()` casts arbitrary buffers to `unsigned int *` for larger signatures, which can be unaligned on strict-alignment platforms.
- Log paths are based on the raw filename prefix before `-journal`; unusual names or embedded NULs are not supported.
- The log object pair uses `zFilename==NULL` as a journal sentinel. `vlogLogClose` does not free through the journal entry, so reference accounting must stay paired with main entry lifetime.
- CSV writes are not mutex-protected around `fprintf`, but the design avoids cross-process sharing by creating unique log files.
- `vlogUnlock` logs before delegating and records result `0`, so unlock failures are not represented like other methods.
- `xDelete` and `xAccess` call `vlogLogOpen` after the real operation, which can create log files for paths that were only probed or deleted.

## Test Signals

Useful signals include loading/registering the VFS, opening a database, performing reads/writes/transactions, and verifying that a `*-debuglog-*` CSV appears with `IDENT`, `OPEN`, `READ`, `WRITE`, `SYNC`, lock, file-control, and `CHNGCTR-*` rows. Error-path tests should cover failed `xOpen`, failed log file creation, rollback-journal operations sharing the main log, WAL files not being logged, `SQLITE_FCNTL_VFSNAME`, and importability of rows by the SQLite shell `.import` command.
