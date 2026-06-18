# Research: sources/storage-engines/sqlite/ext/misc/vfsstat.c

## Purpose

`vfsstat.c` is a loadable SQLite extension that installs a VFS shim and an eponymous virtual table named `vfsstat`. The shim counts VFS I/O and selected VFS-level calls by file category, while the virtual table exposes the counters as rows `(file, stat, count)` and allows `UPDATE` of `count` to reset or seed values.

It is diagnostic code for measuring database, journal, WAL, temporary, and miscellaneous VFS activity. The header explicitly warns that counters are incremented without mutex protection, so multi-threaded use can produce inaccurate statistics.

## Important APIs, Types, And Functions

- `sqlite3_vfsstat_init()` is the extension entry point. It initializes the extension API, wraps the default VFS, registers the wrapper as default, creates the `vfsstat` module on the current connection, registers it as an auto-extension for future connections, and returns `SQLITE_OK_LOAD_PERMANENTLY`.
- `VStatVfs` stores the wrapper `sqlite3_vfs` and parent VFS pointer.
- `VStatFile` stores the wrapper file, real file pointer, and `eFiletype`.
- `aVfsCnt[VFSSTAT_MXCNT]` is the global counter matrix indexed by `STATCNT(filetype, stat)`.
- File-type constants distinguish database, rollback journal, WAL, master journal, sub-journal, temp database, temp journal, transient DB, and `*` for VFS-level operations.
- File methods count reads, read bytes on successful reads, writes, written bytes on successful writes, syncs, opens, and lock/unlock/check-reserved-lock operations.
- VFS methods count `xAccess`, `xDelete`, `xFullPathname`, `xRandomness`, `xSleep`, and both current-time variants against the `*` file type.
- `vstattabColumn`, `vstattabFilter`, `vstattabNext`, `vstattabEof`, and `vstattabUpdate` implement the virtual-table view and reset/update behavior.

## Control Flow

When the extension is loaded, the current default VFS is captured and the `vfslog`-named wrapper is registered as the new default. Every subsequent `xOpen` delegates to the parent VFS, classifies the file from SQLite open flags, increments the `open` counter, and installs `vstat_io_methods` on success.

Wrapped I/O methods delegate first, then update counters. Successful `xRead` and `xWrite` add byte counts; request counters are incremented regardless of result. Shared-memory and mmap methods are forwarded without counting. `xFileControl(SQLITE_FCNTL_VFSNAME)` prepends `vstat/` to the underlying name.

The virtual table is eponymous and scan-only. `xFilter` starts at counter index 0, `xNext` increments the raw counter index, `xColumn` maps the index to file/stat/count labels, and `xEof` stops at `VFSSTAT_nFile * VFSSTAT_nStat`. `xUpdate` rejects inserts/deletes, rowid changes, non-integer count values, negative counts, and out-of-range rowids, then writes directly to `aVfsCnt`.

## State And Persistence Behavior

All state is process-global and in-memory. Counters are not persisted to disk and are reset when the process exits or the extension image is unloaded. `sqlite3_auto_extension()` makes the virtual-table module available to future connections in the process, but it does not make counter updates transactional; `UPDATE vfsstat SET count=0` mutates global state immediately through `xUpdate`.

The VFS wrapper remains registered permanently after load because the init function returns `SQLITE_OK_LOAD_PERMANENTLY`. Counter labels are static string arrays, and the table object/cursors contain only scan position.

## Dependencies And Integration Points

The file uses the SQLite loadable-extension ABI, VFS ABI version 2, I/O method version 3, virtual-table APIs including `sqlite3_declare_vtab`, `sqlite3_create_module`, and `sqlite3_auto_extension`, and SQLite memory helpers. It relies on SQLite open flags to infer file type. Integration is broad because the wrapper becomes the default VFS for the process after load.

## Risks And Edge Cases

- The wrapper VFS name is `"vfslog"`, not `"vfsstat"`, which can confuse diagnostics or collide with `vfslog.c` if both are loaded.
- Counter increments are unsynchronized and can race in multi-threaded use.
- Mmap `xFetch`/`xUnfetch` and WAL shared-memory methods are forwarded but not counted, so statistics are incomplete for mmap-heavy or WAL workloads.
- `vstatOpen` increments `open` even when the underlying open fails, then sets `pMethods` to NULL on failure.
- `xBestIndex` ignores constraints, so filtered queries scan all counters and SQLite applies filtering itself.
- `xUpdate` exposes raw rowid-indexed counter mutation; labels are not validated by file/stat names.
- Returning `SQLITE_OK_LOAD_PERMANENTLY` means the extension is meant to remain installed for process lifetime.

## Test Signals

Tests should load the extension, open a database after load, run read/write/sync/lock-producing SQL, query `SELECT * FROM vfsstat WHERE count>0`, reset with `UPDATE vfsstat SET count=0`, and confirm counters change as expected. Coverage should include each file type flag where feasible, failed opens, WAL mode limitations, auto-extension registration for later connections, and `SQLITE_FCNTL_VFSNAME` output.
