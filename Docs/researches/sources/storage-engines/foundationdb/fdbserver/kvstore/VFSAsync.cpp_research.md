# sources/storage-engines/foundationdb/fdbserver/kvstore/VFSAsync.cpp

## Purpose
This file implements the `fdb_async` SQLite VFS on top of FoundationDB's `IAsyncFile` abstraction. It adapts SQLite file, locking, shared-memory, randomness, sleep, time, and path callbacks to Flow/FDB primitives so SQLite-backed kvstore code can run against the same asynchronous filesystem and simulation fault model.

## Important APIs, Types, And Functions
`vfsAsync()` returns a static `sqlite3_vfs` with all callback pointers. `asyncOpen` constructs a placement-new `VFSAsyncFile`, maps SQLite open flags to `IAsyncFile` flags, opens the file through `IAsyncFileSystem`, and installs a static `sqlite3_io_methods` table. File methods include `asyncClose`, `asyncRead`, `asyncReadZeroCopy`, `asyncReleaseZeroCopy`, `asyncWrite`, `asyncTruncate`, `asyncSync`, `VFSAsyncFileSize`, `asyncLock`, `asyncUnlock`, `asyncCheckReservedLock`, `VFSAsyncFileControl`, `asyncSectorSize`, and `asyncDeviceCharacteristics`.

`SharedMemoryInfo` and callbacks `asyncShmMap`, `asyncShmLock`, `asyncShmBarrier`, and `asyncShmUnmap` implement SQLite WAL shared-memory behavior in process memory. Path and environment callbacks include `asyncAccess`, `asyncFullPathname`, `vfsAsyncIsOpen`, dynamic-library no-ops, `asyncRandomness`, `asyncSleep`, `asyncCurrentTime`, `asyncCurrentTimeInt64`, and `asyncGetLastError`.

## Control Flow
SQLite enters through `asyncOpen`, which rejects null temp names, masks creation flags because higher-level code pre-creates database files, adds large pages for WAL files and file locking, zeroes the SQLite file memory, constructs `VFSAsyncFile`, and opens the underlying async file. Reads and writes synchronously wait on Flow futures using `waitFor`/`waitForAndGet` because SQLite expects blocking VFS callbacks. Short reads zero-fill the unread tail and return `SQLITE_IOERR_SHORT_READ`. Zero-copy reads request a borrowed buffer from `IAsyncFile`, track debug references, and fall back to SQLite's slow path for short reads.

Shared-memory mapping lazily creates one `SharedMemoryInfo` per filename, allocates fixed-size regions on demand, and returns region pointers to SQLite. Shared/exclusive WAL locks are tracked both globally and per `VFSAsyncFile` bitmask so unlock calls are idempotent even if SQLite asks to unlock locks this handle does not hold. File close destroys the `VFSAsyncFile`; when the last open handle for a filename disappears, any zero-ref shared-memory entry is cleaned up.

## State And Persistence Behavior
Persistent bytes live in the underlying files opened through `IAsyncFile`. Process-local state includes `VFSAsyncFile::filename_lockCount_openCount`, per-file debug counters, per-file chunk size, held shared-memory lock bitmasks, and `SharedMemoryInfo::table`. Shared-memory regions are heap arrays and are not persisted; they are cleaned when the last open file handle for a filename is destroyed and the refcount is zero.

Injected Flow faults are translated into SQLite error codes and stored via `VFSAsyncFile::setInjectedError`. `asyncSleep` integrates with simulation by waiting on the current process shutdown signal as a cancellation source.

## Dependencies And Integration Points
The file depends on SQLite's VFS ABI, `VFSAsync.h`, Flow `IAsyncFile`, `IAsyncFileSystem`, `fdbrpc`, `CoroFlow`, simulator/process info, `AsyncFileReadAhead`, platform path helpers, OS `access/stat/gettimeofday` or Windows file APIs, and Flow tracing/error handling. SQLite users must register the returned VFS with `sqlite3_vfs_register(sqlite3_asyncvfs(), 0)` or equivalent.

## Risks
The VFS is a synchronous wrapper over async APIs, so misuse on an event-loop path could block progress. `asyncDelete` is asserted false and unimplemented. `asyncLock` returns busy for exclusive locks and otherwise mostly trusts SQLite/WAL shared-memory locking, which may not match all SQLite locking modes. Shared-memory is process-local, not interprocess shared memory, so this VFS is suitable for FDB's usage assumptions but not arbitrary multi-process SQLite access. The filename/open-count maps are static and not obviously protected by a mutex outside shared-memory operations. Zero-copy paths rely on balanced release calls; close asserts no outstanding references. Path length is capped by `MAXPATHNAME`.

## Test Signals
Useful tests include read/write/truncate/sync/file-size behavior, short-read zero filling, zero-copy read and release balance, chunk-size and size-hint file controls, WAL shared-memory map/lock/unmap sequences, repeated opens and final shared-memory cleanup, injected read/write/sync/open faults mapping to SQLite codes, simulation sleep cancellation, path canonicalization, and confirmation that SQLite never calls the unimplemented delete path in supported kvstore workflows.
