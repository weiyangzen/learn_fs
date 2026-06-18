# sources/storage-engines/foundationdb/fdbserver/kvstore/VFSAsync.h

## Purpose

`VFSAsync.h` declares the SQLite file-handle object used by FoundationDB's custom SQLite VFS. SQLite receives `sqlite3_file*` handles, but this VFS stores a `VFSAsyncFile` at that address so SQLite file operations can be backed by FoundationDB's `IAsyncFile` abstraction and the Flow network/runtime.

The header is intentionally small but important: it defines the per-file state that `VFSAsync.cpp` uses for SQLite `xOpen`, `xRead`, `xWrite`, `xSync`, WAL shared-memory callbacks, zero-copy reads, chunk-size hints, open-count cleanup, and simulation error attribution.

## Important APIs, Types, and Functions

`VFSAsyncFile` is the central type. Its first member is `sqlite3_file base`, which is required because SQLite treats a `sqlite3_file*` as the base object and the VFS implementation casts it back to `VFSAsyncFile*`.

The key fields are:

- `flags`: original SQLite open flags.
- `filename`: path used for the underlying async file and for process-local lock/shared-memory bookkeeping.
- `Reference<IAsyncFile> file`: underlying FoundationDB async file; the implementation calls `read`, `write`, `truncate`, `sync`, `size`, `readZeroCopy`, and `releaseZeroCopy`.
- `pLockCount` and `lockLevel`: database-file locking state. `pLockCount` points into the static `filename_lockCount_openCount` entry for this filename.
- `sharedMemory`, `sharedMemorySharedLocks`, and `sharedMemoryExclusiveLocks`: per-handle state for SQLite WAL shared-memory regions and locks.
- `debug_zcrefs`, `debug_zcreads`, and `debug_reads`: debug counters used to assert zero-copy buffers are released before close and to track read paths.
- `chunkSize`: SQLite `SQLITE_FCNTL_CHUNK_SIZE` value; truncation rounds size hints to this boundary.

`VFSAsyncFile(std::string const& filename, int flags)` initializes filename-scoped bookkeeping and debug/chunk fields. `~VFSAsyncFile()` decrements the filename open count and, for the last open handle, erases the filename entry and removes process-local shared-memory state.

`filename_lockCount_openCount` maps a filename to `{lockCount, openCount}`. The constructor increments `openCount`; the destructor decrements it. The lock-count pointer is used by reserved-lock checks, although the current file-lock callbacks are minimal and shared-memory locking carries most WAL coordination.

`setInjectedError(int64_t rc)` stores the latest injected SQLite-facing return code in `g_network` under `INetwork::enSQLiteInjectedError` and emits `VFSSetInjectedError`. VFS callbacks call this when they catch a Flow `Error` marked as an injected fault.

`checkInjectedError()` reads that global and combines it with `g_simulator->checkInjectedCorruption()`. `KeyValueStoreSQLite` uses it when SQLite returns an error so simulation can classify the surfaced `io_error` as injected even though SQLite does not preserve FoundationDB `Error` metadata through its C callback boundary.

## Control Flow

The normal open path is implemented in `VFSAsync.cpp`: SQLite calls the registered VFS `xOpen`, the implementation placement-news a `VFSAsyncFile` into SQLite's allocated `sqlite3_file` memory, opens `IAsyncFileSystem::filesystem()->open(filename, flags | OPEN_LOCK, 0600)`, assigns the SQLite `sqlite3_io_methods`, and returns `SQLITE_OK`.

Subsequent SQLite file callbacks cast the `sqlite3_file*` back to `VFSAsyncFile*` and synchronously wait on Flow futures:

- reads call `file->read`; short reads zero-fill the remainder and return `SQLITE_IOERR_SHORT_READ` as SQLite expects.
- zero-copy reads call `file->readZeroCopy`, increment `debug_zcrefs`, and require a matching `releaseZeroCopy`.
- writes call `file->write`.
- truncates optionally round to `chunkSize` and call `file->truncate`.
- syncs call `file->sync`.
- file-size queries call `file->size`.
- file-control handles chunk-size and size-hint opcodes.

Close calls the destructor after asserting all zero-copy references were released. This is a critical ownership boundary because the memory occupied by `VFSAsyncFile` is owned by SQLite, while its C++ members and references must be explicitly constructed and destroyed.

WAL shared-memory control flow is also based on fields declared here. `asyncShmMap` creates or looks up process-local `SharedMemoryInfo` by `filename`, allocates regions on demand, and stores the pointer in `sharedMemory`. `asyncShmLock` compares and updates the per-handle lock bitmasks against shared counters. `asyncShmUnmap` drops this file handle's shared-memory association; final cleanup is deferred until the last `VFSAsyncFile` for the filename is destroyed.

## State and Persistence Behavior

Persistent database and WAL bytes live in the underlying `IAsyncFile`. The header's state is process-local metadata around those files: open counts, lock counts, debug counters, WAL shared-memory pointers, and simulation error attribution.

SQLite database creation is not performed in this VFS open path. `KeyValueStoreSQLite` creates the database and WAL first using `IAsyncFileSystem` atomic-write flags, then lets SQLite open them through this VFS. `VFSAsync.cpp` deliberately masks out SQLite create/exclusive flags and always adds `IAsyncFile::OPEN_LOCK`.

`chunkSize` affects physical file size behavior: size hints and truncates are rounded upward when SQLite configures a nonzero chunk size. `KeyValueStoreSQLite::open` sets this with `sqlite3_file_control`, using knob-driven production and simulation values.

The shared-memory implementation is in-memory, not a durable shm file. It is keyed by absolute filename and cleaned when the last open handle for that filename is destroyed. This makes simulation cleanup important: leaked or stale shared-memory state can cause later SQLite WAL locking failures or corruption-like behavior after simulated process death.

Injected-error state is stored globally in the current `INetwork`, not in a file object. That design handles SQLite API calls that open, fail, and close VFS files before the higher-level caller can inspect a file object, but it is approximate: a later unrelated SQLite error can be classified as injected if the global marker remains set.

## Dependencies and Integration Points

The header depends on SQLite (`sqlite3.h`), Flow async file primitives (`flow/IAsyncFile.h`), and simulation globals (`fdbrpc/simulator.h`). It also uses `Reference`, `TraceEvent`, `g_network`, `g_simulator`, and `INetwork::enSQLiteInjectedError` from FoundationDB runtime headers included directly or transitively.

Primary implementation is `VFSAsync.cpp`, which defines the SQLite VFS named `fdb_async`, the I/O callbacks, shared-memory helper type, `vfsAsync()`, and `vfsAsyncIsOpen()`.

Primary consumer is `KeyValueStoreSQLite.cpp`. It includes this header, registers `vfsAsync()` as SQLite's default VFS, opens database and WAL files with `IAsyncFileSystem` before SQLite open, sets SQLite file-control chunk size, checks `vfsAsyncIsOpen()` assertions around open/close behavior, and calls `VFSAsyncFile::checkInjectedError()` in SQLite error paths.

`IAsyncFile` integration is especially important for zero-copy reads. The `IAsyncFile` contract says `readZeroCopy` may fail and callers should fall back to normal reads; the VFS follows that pattern by returning a SQLite read error so SQLite can use the slower read path. The same contract requires every successful zero-copy read to be released, which is enforced by `debug_zcrefs` on close.

## Risks and Edge Cases

`VFSAsyncFile` must remain layout-compatible with SQLite: `sqlite3_file base` must stay first, and `vfsAsync()` must report `sizeof(VFSAsyncFile)` as `szOsFile`. Adding fields changes the memory size SQLite must allocate.

The injected-error global is intentionally imprecise. It improves simulation attribution through SQLite's C API, but non-injected errors after an injected VFS error can be misclassified.

Shared-memory state is process-local and keyed by filename. It is protected by a mutex, but cleanup relies on correct open-count tracking and balanced SQLite close/unmap behavior. Assertions around `refcount == 0` and `deleteFlag` indicate unexpected SQLite lifetime behavior should be treated seriously.

The file-lock callbacks are minimal: `asyncLock` rejects exclusive locks with `SQLITE_BUSY` and otherwise returns success, while WAL shared-memory locks do the meaningful coordination. Any SQLite journal-mode change away from the expected WAL path could expose underimplemented locking behavior.

Zero-copy reads have strict lifetime rules. If SQLite or a future callback path fails to call release, close asserts. If a short zero-copy read occurs, the implementation releases the buffer and returns `SQLITE_IOERR_SHORT_READ` because it cannot zero-fill pinned memory.

Header-level static methods assume simulation globals are available when used. `checkInjectedError()` directly calls `g_simulator->checkInjectedCorruption()`, so callers already gate this path to simulation contexts.

## Test Signals

Useful behavioral signals are SQLite store tests that open, close, checkpoint, and validate WAL databases through `KeyValueStoreSQLite`; failures often surface as `DiskError`, `VFSAsyncFileOpenError`, `VFSAsyncFileSyncError`, or `BTreeIntegrityCheckResults`.

Simulation fault-injection tests should show injected I/O errors being converted to SQLite return codes by VFS callbacks and then reclassified by `KeyValueStoreSQLite::checkError()` through `VFSAsyncFile::checkInjectedError()`.

WAL lifecycle tests should exercise `vfsAsyncIsOpen(filename)` assertions after checksum scans and store destruction, confirming shared-memory tables are cleaned after the last handle closes.

Chunk-size tests should verify `SQLITE_FCNTL_CHUNK_SIZE` and `SQLITE_FCNTL_SIZE_HINT` produce rounded truncation sizes without corrupting SQLite page layout.

Zero-copy coverage should include successful cached reads, fallback on short or unsupported zero-copy reads, and balanced release paths so `debug_zcrefs` remains zero at close.
