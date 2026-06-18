# Research: sources/storage-engines/sqlite/src/os_unix.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008776`: lines 1-7629, `Docs/researches/chunks/subset-b-008776_research.md`
- `subset-b-008777`: lines 7630-8604, `Docs/researches/chunks/subset-b-008777_research.md`

## Chunk Research

### subset-b-008776: lines 1-7629

# sources/storage-engines/sqlite/src/os_unix.c lines 1-7629

## Scope

This chunk covers the beginning and most of the Unix SQLite VFS implementation: platform feature selection, syscall indirection, file descriptor helpers, POSIX and alternate locking implementations, common `sqlite3_file` methods, WAL shared-memory support, mmap fetch/unfetch support, `sqlite3_io_methods` tables, and the first part of `sqlite3_vfs` methods through the start of macOS proxy-locking helpers. The proxy-locking implementation continues after line 7629, beginning inside `proxyGetHostID()`.

## Purpose

`os_unix.c` adapts SQLite's portable VFS and pager expectations to Unix-like operating systems. The code in this range provides durable file I/O, advisory locking, WAL shared-memory coordination, mmap reads, temporary file naming, path canonicalization, dynamic-library loading, randomness, and time services. It contains multiple VFS locking variants because Unix filesystems differ significantly: normal POSIX byte-range locks, no locking, dot-directory locks, `flock()`, VxWorks named semaphores, Apple AFP/NFS variants, and the setup for macOS proxy locking.

## Important Types and State

- `unixFile` subclasses `sqlite3_file`. It owns the OS file descriptor `h`, selected `sqlite3_io_methods`, VFS pointer, path, current SQLite lock level, control flags, last errno, locking-specific context, pending reusable fd storage, WAL shared-memory pointer, chunk size, sector/device characteristics, optional mmap fields, Apple filesystem flags, setlk timeout state, and VxWorks file id state.
- `UnixUnusedFd` stores file descriptors that cannot be closed immediately because closing any descriptor for the same inode can drop POSIX locks owned by the process. They are retained on `unixInodeInfo.pUnused` and closed when the final lock clears.
- `unixFileId` keys a file by device and inode, or by a canonical VxWorks file id.
- `unixInodeInfo` is the central per-open-inode coordination object. It tracks process-local lock state (`nShared`, `nLock`, `eFileLock`, `bProcessLock`), deferred fds, WAL shared-memory node, refcount, linked-list membership, and platform-specific lock state. Its lock fields are protected by `pLockMutex`; the global `unixBigLock` protects list/refcount operations.
- `unixShmNode` represents one WAL index shared-memory file per process and inode. It holds the `-shm` fd, mapped regions, region size/count, read-only/unlocked flags, process-local lock counters in `aLock[]`, optional per-slot mutexes for blocking-lock builds, and a list/refcount of `unixShm` connections.
- `unixShm` represents one connection's WAL shared-memory handle. It records the owning node, sibling list link, diagnostic id, and bitmasks of shared/exclusive WAL locks held by that connection.
- `afpLockingContext` and `proxyLockingContext` carry platform-specific path and secondary-file state for Apple AFP/proxy locking.
- Global state includes `aSyscall[]` for overrideable syscalls, `randomnessPid` to detect forked PRNG reuse, `unixBigLock`, `inodeList`, VxWorks file-id lists, sync counters under `SQLITE_TEST`, temp-dir array `azTempDirs[]`, and test hook `sqlite3_current_time`.

## Syscall and Utility Layer

`aSyscall[]` wraps important OS calls (`open`, `close`, `stat`, `fcntl`, `pread/pwrite`, `fchmod`, `fallocate`, `unlink`, `mmap`, `readlink`, `ioctl`, etc.) behind macros such as `osOpen`, `osFcntl`, and `osMmap`. `unixSetSystemCall()`, `unixGetSystemCall()`, and `unixNextSystemCall()` expose this indirection through the VFS so tests and sandboxed hosts can inject replacements.

The low-level helpers harden platform behavior:

- `robust_open()` retries `open()` on `EINTR`, adds close-on-exec where possible, avoids descriptors below `SQLITE_MINIMUM_FILE_DESCRIPTOR`, applies exact permissions for WAL/journal creation, and logs suspicious low-fd allocation.
- `robust_close()` logs but does not retry failed `close()` calls because the descriptor may already be reused after `EINTR`.
- `robust_ftruncate()` retries on `EINTR` and ignores unsafe large truncates on Android's 32-bit `ftruncate`.
- `unixLogErrorAtLine()` preserves `errno`, formats platform error text, and logs SQLite extended error codes with source line and path.
- `sqliteErrorFromPosixError()` maps lock-related POSIX errors into `SQLITE_BUSY`, `SQLITE_PERM`, or the caller-supplied IOERR.
- `robustFchown()` only calls `fchown()` as root to avoid non-root security-log noise.
- Debug support includes POSIX lock introspection through `/proc/PID/fdinfo/FD` (`unixPosixAdvisoryLocks()`), optional fcntl tracing (`lockTrace()`), and lock-name formatting.

## Locking Control Flow

The POSIX path is the full-concurrency implementation:

1. `fillInUnixFile()` selects a locking method and, for POSIX/NFS/AFP/VxWorks semaphore styles, attaches or creates a `unixInodeInfo` via `findInodeInfo()`.
2. `unixLock()` enforces SQLite's lock state machine: `NO_LOCK -> SHARED`, `SHARED -> RESERVED`, `SHARED/RESERVED -> PENDING -> EXCLUSIVE`.
3. For `SHARED`, it first read-locks `PENDING_BYTE`, read-locks the shared range, then unlocks `PENDING_BYTE`.
4. For `RESERVED`, it write-locks `RESERVED_BYTE`.
5. For `EXCLUSIVE`, it may first write-lock `PENDING_BYTE`, then write-lock the entire shared range.
6. Process-local state in `unixInodeInfo` prevents two connections in the same process from defeating POSIX locks, whose semantics are process-wide rather than descriptor-wide.
7. `posixUnlock()` downgrades to shared or no-lock, handles the Apple/NFS split-range downgrade workaround, decrements process-local counters, and drains deferred fd closes when `nLock` reaches zero.
8. `unixClose()` unlocks, defers descriptor close if locks remain on the same inode, releases inode info, unmaps WAL/mmap state, and clears `unixFile`.

Alternate locking styles collapse or adapt this model:

- `nolock*` functions ignore all locking and are only safe for read-only or externally serialized databases.
- `dotlock*` maps all SQLite lock states to an exclusive directory named `<db>.lock`. Unlock to `NO_LOCK` removes the directory; stale directories after crashes are a known operational risk.
- `flock*` maps all held lock states to `LOCK_EX|LOCK_NB` and `LOCK_UN`, reducing concurrency to a single process/connection class.
- VxWorks `semX*` maps lock states to a named POSIX semaphore created from the canonical file id.
- Apple AFP uses `fsctl(afpfsByteRangeLock2FSCTL)` to emulate SQLite byte-range locks, choosing a random shared byte for `SHARED` and a whole shared range for `EXCLUSIVE`.
- Apple NFS reuses POSIX locking but uses the special split downgrade path.
- `autolockIoFinderImpl()` chooses a macOS locking method from filesystem type and an `F_GETLK` capability probe. `vxworksIoFinderImpl()` similarly chooses POSIX or semaphore locking.

## File I/O Behavior

`unixRead()` and `unixWrite()` implement the pager-facing I/O contract.

- Reads use `pread/pread64` when available, else `lseek()+read()`. Interrupted reads are retried; partial positive reads continue until EOF or completion. Short reads zero-fill the unread tail and return `SQLITE_IOERR_SHORT_READ`. Certain low-level errors (`ERANGE`, `EIO`, `ENXIO`, `EDEVERR`) are reported as corrupt filesystem signals.
- Writes use `pwrite/pwrite64` or `lseek()+write()`, loop over short writes, translate ENOSPC or simulated disk-full to `SQLITE_FULL`, and otherwise return `SQLITE_IOERR_WRITE`.
- Debug builds track whether a normal database write also changes bytes 24-27, the SQLite database change counter. Unlock assertions rely on this to catch stale-cache corruption risks.
- `unixSync()` calls `full_fsync()`, optionally using `F_FULLFSYNC` on Apple, `fdatasync()` elsewhere, or fsync fallbacks. For new journal/WAL files it can fsync the containing directory once via `UNIXFILE_DIRSYNC`.
- `unixTruncate()` honors `SQLITE_FCNTL_CHUNK_SIZE` by rounding truncation up to a chunk boundary and adjusts mmap visibility if the file shrinks.
- `unixFileSize()` uses `fstat()` and hides the one-byte OS X msdos filesystem workaround as size zero.
- `fcntlSizeHint()` preallocates space using `posix_fallocate()` when available, otherwise writes one byte at block ends; it can also grow/remap mmap state.

## File Controls, Capabilities, and mmap

`unixFileControl()` handles important SQLite file-control operations:

- Linux F2FS batch atomic write hooks (`BEGIN_ATOMIC_WRITE`, `COMMIT_ATOMIC_WRITE`, `ROLLBACK_ATOMIC_WRITE`) via `ioctl()` when enabled.
- `SQLITE_FCNTL_NULL_IO`, `LOCKSTATE`, `LAST_ERRNO`, `CHUNK_SIZE`, `SIZE_HINT`, `PERSIST_WAL`, `POWERSAFE_OVERWRITE`, `VFSNAME`, `TEMPFILENAME`, `HAS_MOVED`, `EXTERNAL_READER`, and debug/filestat JSON.
- Blocking lock controls when `SQLITE_ENABLE_SETLK_TIMEOUT` is compiled in.
- `SQLITE_FCNTL_MMAP_SIZE`, which updates `mmapSizeMax`, refuses remap while `nFetchOut>0`, and remaps existing regions when possible.
- Apple proxy lock controls are forwarded to `proxyFileControl()` outside this chunk's fully visible implementation.

`setDeviceCharacteristics()` reports sector size and capability flags. Generic Unix defaults to `SQLITE_DEFAULT_SECTOR_SIZE`, `SQLITE_IOCAP_SUBPAGE_READ`, optional `SQLITE_IOCAP_POWERSAFE_OVERWRITE`, and optional F2FS batch atomic capability. QNX has filesystem-specific capability detection for tmpfs, etfs, qnx6, qnx4, and dos-like filesystems.

The mmap path is optional under `SQLITE_MAX_MMAP_SIZE>0`:

- `unixMapfile()` calculates target mapping size from file size or requested bytes, clamps to `mmapSizeMax`, and avoids remapping while xFetch references are outstanding.
- `unixRemapfile()` tries to reuse or extend an existing mapping via `mremap()` or adjacent `mmap()`, falls back to a new mapping, and disables future mmap attempts on failure.
- `unixFetch()` returns a direct pointer only if the mapping covers the requested bytes plus a 256-byte EOF safety buffer.
- `unixUnfetch()` releases references or unmaps the entire file when called with a null pointer.

## WAL Shared Memory

When WAL is enabled, `unixShmMap()`, `unixShmLock()`, `unixShmBarrier()`, and `unixShmUnmap()` fill the version-3 `sqlite3_io_methods` shared-memory slots.

`unixOpenSharedMemory()` creates or reuses one `unixShmNode` for the database inode, derives the `-shm` path (or `SQLITE_SHM_DIRECTORY` path), opens it read-write or read-only, copies ownership from the database when possible, and calls `unixLockSharedMemory()` before adding a new `unixShm` connection.

`unixLockSharedMemory()` coordinates the deadman-switch byte (`UNIX_SHM_DMS`). The first writer takes an exclusive DMS lock, truncates the `-shm` file to 3 bytes as an intentional marker, then downgrades to a shared DMS lock. Read-only `readonly_shm=1` connections that cannot initialize return `SQLITE_READONLY_CANTINIT` and mark the node as unlocked for a later retry.

`unixShmMap()` extends and maps 32 KiB regions, using page-aligned mapping batches (`unixShmRegionPerMap()`). To reduce SIGBUS risk, it writes the last byte of each newly allocated OS page before mapping. In `unix-excl` mode, it simulates shared memory with heap allocations instead of a `-shm` file.

`unixShmLock()` keeps process-local lock accounting in `aLock[]` and per-connection masks while applying POSIX locks over WAL slots. It prohibits shared-to-exclusive and exclusive-to-shared transitions, handles shared refcounts within one process, and uses per-slot mutexes in setlk-timeout builds to avoid deadlocks between blocking lock attempts. `unixFcntlExternalReader()` uses `F_GETLK` over read-lock slots to detect other-process WAL readers. `unixIsSharingShmNode()` checks the DMS byte to make final WAL cleanup more robust when database locks were accidentally broken.

`unixShmUnmap()` unlinks the connection from the node, decrements the node refcount under `unixBigLock`, optionally deletes the `-shm` file, and purges mappings, mutexes, fd, and node memory when the refcount reaches zero.

## VFS Opening and Path Behavior

`unixOpen()` is the central VFS `xOpen` method.

- It validates SQLite open-flag combinations and file type flags.
- It resets SQLite's PRNG after fork detection using `randomnessPid`.
- Main database opens may reuse a deferred descriptor from `findReusableFd()`.
- Temporary files use `O_TMPFILE` where available, else `unixGetTempname()` in one of `sqlite3_temp_directory`, `SQLITE_TMPDIR`, `TMPDIR`, `/var/tmp`, `/usr/tmp`, `/tmp`, or `.`.
- It builds POSIX open flags with large-file, binary, and no-follow behavior, falls back from read-write to read-only where appropriate, and reports unwritable journal directories as `SQLITE_READONLY_DIRECTORY`.
- `findCreateFileMode()` copies permissions and ownership from the database to WAL/main-journal files, uses `0600` for delete-on-close files, and supports URI `modeof=`.
- Delete-on-close files are unlinked immediately unless platform configuration delays unlink until close.
- It detects msdos/exfat filesystems to work around OS X zero-size inode bugs.
- It marks non-main-database files as `UNIXFILE_NOLOCK`, marks new journals/WALs for directory sync, records URI and readonly flags, and optionally transforms to proxy locking on macOS non-local files.

`fillInUnixFile()` initializes `unixFile`, applies URI `psow`, marks `unix-excl`, resolves the selected I/O method through the VFS finder, allocates any locking context, finds inode state where needed, sets `pMethods`, and verifies database file integrity assumptions.

Path and filesystem helpers include:

- `unixDelete()` unlinks a path and optionally fsyncs its directory.
- `unixAccess()` implements existence and read-write access checks. Existence ignores zero-size regular files.
- `DbPath`, `appendOnePathElement()`, and `appendAllPathElements()` canonicalize paths, remove `.` and `..`, resolve symlinks through `lstat/readlink`, and limit symlink expansion.
- `unixFullPathname()` prefixes relative paths with cwd, canonicalizes them, and returns `SQLITE_OK_SYMLINK` if symlinks were resolved.

## Other VFS Methods

The chunk includes the dynamic extension hooks (`unixDlOpen()`, `unixDlError()`, `unixDlSym()`, `unixDlClose()`), unless load extensions are omitted. `unixDlSym()` uses an indirect function-pointer variable to work around C90/pedantic concerns about casting `void*` to function pointers.

`unixRandomness()` zero-initializes the buffer for valgrind cleanliness, records the current pid, then uses `/dev/urandom` when not in deterministic test mode. If that fails, it falls back to current time plus pid.

`unixSleep()` uses `nanosleep()`, `usleep()`, or `sleep()` depending on platform macros. `unixCurrentTimeInt64()` returns Julian milliseconds using `gettimeofday()`, VxWorks `clock_gettime()`, or `time()`, with `sqlite3_current_time` test override. Deprecated `unixCurrentTime()` converts the int64 value to Julian days. `unixGetLastError()` returns `errno`.

## Integration Points

- SQLite core/pager interacts through `sqlite3_io_methods` created by the `IOMETHODS` macro and through VFS methods such as xOpen, xDelete, xAccess, xFullPathname, xRandomness, xSleep, and xCurrentTime.
- WAL code depends on xShmMap/xShmLock/xShmBarrier/xShmUnmap and on `SQLITE_FCNTL_EXTERNAL_READER`.
- URI parameters alter behavior: `psow`, `readonly_shm`, and `modeof`.
- Compile-time flags reshape behavior heavily: `SQLITE_ENABLE_LOCKING_STYLE`, `SQLITE_OMIT_WAL`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_ENABLE_SETLK_TIMEOUT`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_MMAP_READWRITE`, `SQLITE_DISABLE_DIRSYNC`, `SQLITE_NO_SYNC`, `SQLITE_WASI`, `OS_VXWORKS`, Apple-specific macros, and QNX macros.
- Runtime environment influences temp directories and macOS proxy selection (`SQLITE_TMPDIR`, `TMPDIR`, `SQLITE_FORCE_PROXY_LOCKING`, `LOCKPROXYDIR`).
- Test and fault-injection infrastructure relies on syscall replacement, `SimulateIOError`, `SimulateDiskfullError`, sync counters, deterministic randomness, current-time override, lock tracing, and FILESTAT JSON.

## Persistence and Durability Behavior

Persistent effects include main database/journal/WAL reads and writes, `ftruncate()`, allocation writes for size hints and SHM extension, directory sync for newly created journals/WALs, `-shm` file creation/truncation/mapping, optional `-shm` unlink on unmap, dotlock directory creation/removal, VxWorks semaphore creation, and proxy lock/conch file creation setup. The code is careful to preserve journal/WAL permissions and ownership so recovery remains possible across users and root-started processes.

Durability depends on `full_fsync()`, directory fsync, and compile-time options. `SQLITE_NO_SYNC` intentionally weakens durability for tests. The `UNIXFILE_PSOW` flag can reduce pager write amplification by advertising powersafe overwrite.

## Risks and Edge Cases

- POSIX locks are process-scoped. Closing an unrelated descriptor on the same inode can drop locks; deferred `UnixUnusedFd` handling and reusable fd lookup are critical.
- `unixBigLock` must be acquired before inode `pLockMutex` when both are needed. Reversing this can deadlock.
- No-lock, dotlock, flock, semaphore, AFP, and proxy-related modes reduce or change concurrency semantics. Misconfiguration can cause busy errors or corruption if external serialization assumptions are false.
- WAL shared-memory correctness relies on DMS and per-slot lock discipline. False negatives in `unixIsSharingShmNode()` reduce cleanup robustness; false positives leave WAL/SHM files behind or block transition out of WAL.
- mmap is disabled after mapping failures and cannot remap while fetch references are outstanding. Writable mmap depends on `SQLITE_MMAP_READWRITE` and correct invalidation through `xUnfetch(NULL)`.
- `SQLITE_SHM_DIRECTORY` can make incompatible builds that corrupt databases if different processes choose different SHM locations.
- Symlink resolution has explicit limits, but canonicalization buffers are bounded by VFS path limits; path construction errors map to `SQLITE_CANTOPEN_BKPT`.
- `unixAccess(SQLITE_ACCESS_EXISTS)` treats zero-size regular files as nonexistent, matching SQLite semantics but surprising for generic filesystem expectations.
- Proxy locking is only partially visible in this chunk; path creation and proxy-file open helpers are covered, while host-id lookup and conch/proxy lock operations continue in later lines.

## Test Signals

Relevant tests should exercise:

- Syscall override APIs and injected failures for `open`, `fcntl`, `read`, `write`, `mmap`, `openDirectory`, and `readlink`.
- Lock transition matrix for POSIX locks, including same-process multiple connections, deferred close/reuse, reserved-lock checks, exclusive upgrade busy paths, `unix-excl`, and WAL sharing checks.
- Alternate lock methods where compiled: dotlock stale directory behavior, flock exclusive serialization, VxWorks semaphore fallback, Apple AFP/NFS/autolock selection, and proxy transformation setup.
- Short reads zero-fill buffers; write loops handle partial writes, ENOSPC, and simulated disk-full.
- Sync counters and directory fsync behavior for rollback journals and WAL files.
- Permission/ownership propagation for WAL and main journal files, including root-owned database scenarios.
- Temp file generation through env vars and `O_TMPFILE` fallback.
- WAL shared-memory mapping extension, read-only SHM initialization failure, DMS lock initialization, per-slot lock masks, external-reader detection, and unmap cleanup.
- mmap fetch/unfetch reference accounting, remap refusal while fetched, and fallback after mmap failure.
- Path canonicalization with relative paths, symlinks, symlink loops, and buffer exhaustion.
- Randomness fork detection, deterministic `SQLITE_TEST` behavior, sleep/current-time hooks, and dynamic library error reporting.

### subset-b-008777: lines 7630-8604

# sources/storage-engines/sqlite/src/os_unix.c lines 7630-8604

## Scope

This chunk covers the end of SQLite's Unix VFS implementation. The first major section is the Apple-only proxy-locking implementation for AFP-style deployments, where database locks are redirected through a local proxy lock file coordinated by a "conch" file beside the database. The second section is `sqlite3_os_init()` and `sqlite3_os_end()`, the public Unix OS interface entry points that register available Unix VFS names, allocate static VFS mutexes, validate shared-memory lock layout assumptions, and initialize temporary-file directory state.

## Purpose

- Maintain and acquire proxy-locking conch files that record the owning host id and the selected local proxy lock-file path.
- Detect and break stale conch locks when the same host id still owns an unchanged conch file after retry delays.
- Transform an already-open `unixFile` into a proxy-locking file by replacing its `sqlite3_io_methods` table and preserving the original methods/context for close-time restoration.
- Expose `SQLITE_FCNTL_GET_LOCKPROXYFILE` and `SQLITE_FCNTL_SET_LOCKPROXYFILE` behavior through proxy-file control.
- Implement proxy `xCheckReservedLock`, `xLock`, `xUnlock`, and `xClose` by first taking the conch and then delegating real byte-range locking to the proxy lock file.
- Register the platform-appropriate Unix VFS implementations under names such as `unix`, `unix-none`, `unix-dotfile`, `unix-excl`, `unix-posix`, `unix-flock`, `unix-afp`, `unix-nfs`, and `unix-proxy`.
- Set up Unix VFS global mutex pointers and temp-file directory state at SQLite initialization, and clear mutex globals at shutdown.

## Important APIs, Types, And Functions

- `proxyGetHostID()` finishes in this chunk. On builds with `HAVE_GETHOSTUUID`, it calls `gethostuuid()` with a one-second timeout, reports `errno` through `pError`, and returns `SQLITE_IOERR` on failure. In `SQLITE_TEST`, `sqlite3_hostid_num` perturbs the first host-id byte to simulate multiple hosts.
- `PROXY_CONCHVERSION`, `PROXY_HEADERLEN`, `PROXY_PATHINDEX`, and `PROXY_MAXCONCHLEN` define the on-disk conch record as a one-byte version, a 16-byte host id, and a path string bounded by `MAXPATHLEN`.
- `proxyBreakConchLock(unixFile *pFile, uuid_t myHostID)` copies the current conch contents to a sibling `-break` file, renames that file over the conch path, replaces the open conch descriptor, and closes the old descriptor. `myHostID` is accepted for call-site symmetry but is unused here; the host-id check happens in `proxyConchLock()`.
- `proxyConchLock(unixFile *pFile, uuid_t myHostID, int lockType)` wraps conch-file `xLock()` calls with retry, modification-time checks, host-id verification, and stale-lock breaking.
- `proxyTakeConch(unixFile *pFile)` is the core conch acquisition routine. It reads or creates the conch payload, chooses or validates the proxy lock path, obtains any needed exclusive conch lock, writes and fsyncs updated conch contents, reopens the database descriptor, opens the proxy lock file, and marks `pCtx->conchHeld`.
- `proxyReleaseConch()` unlocks the conch file back to `NO_LOCK` when the proxy context actually holds it.
- `proxyCreateConchPathname(char *dbPath, char **pConchPath)` derives the conch pathname by inserting a dot before the database basename and appending `-conch`, allocating the result with `sqlite3_malloc64()`.
- `switchLockProxyPath()` changes an existing proxy context to a new explicit proxy path only when the database file is currently unlocked. It closes and frees the old proxy lock file and path before storing the new path.
- `proxyGetDbPathForUnixFile()` reconstructs the database path from the pre-proxy locking context. AFP stores it in `afpLockingContext.dbPath`, dotlock stores a dot-lock path that must be trimmed by `DOTLOCK_SUFFIX`, and other styles store the database path directly.
- `proxyTransformUnixFile()` allocates and initializes `proxyLockingContext`, opens the conch file, handles read-only filesystem lockless mode, stores optional explicit lock-proxy path and database path copies, preserves the old methods/context, and installs `proxyIoMethods`.
- `proxyFileControl()` handles proxy-specific file controls: get lock-proxy file, set/switch lock-proxy file, turn proxy locking on, and reject turning proxy locking off once enabled.
- `proxyCheckReservedLock()`, `proxyLock()`, and `proxyUnlock()` are the lock-related methods in `proxyIoMethods`; each calls `proxyTakeConch()` and delegates to `pCtx->lockProxy` if `conchHeld>0`.
- `proxyClose()` closes the proxy lock file, releases and closes the conch file, frees proxy paths and context, restores the original `lockingContext`/`pMethod`, then calls the original close method.
- `sqlite3_os_init()` builds a static mutable `sqlite3_vfs aVfs[]` array using the local `UNIXVFS` initializer macro and registers every compiled-in Unix VFS with SQLite core.
- `sqlite3_os_end()` clears `unixBigLock` and, on VxWorks, `vxworksMutex`, then returns `SQLITE_OK`.

## Control Flow

`proxyConchLock()` first tries the requested conch-file lock through the conch file's own I/O methods. If it sees `SQLITE_BUSY`, it records the conch modification time, sleeps for 0.5 seconds, and retries. On the second busy result, it fails immediately if the modification time changed. If the timestamp is stable, it reads the conch record and only proceeds when the record is long enough, has `PROXY_CONCHVERSION`, and contains the current host id. It then waits 10 seconds and retries. On the third busy result, it calls `proxyBreakConchLock()` and, when breaking succeeds, reacquires a shared lock first for exclusive-lock requests before requesting the final lock type.

`proxyTakeConch()` returns early when `pCtx->conchHeld` is non-zero, so a held conch or read-only lockless state is stable across later lock calls. Otherwise it obtains the current host id, takes a shared conch lock, and reads the conch record. Short reads or version mismatches set `createConch`, while valid records are compared against the current host id and the configured lock-proxy path.

For `:auto:` proxy paths, a matching host id lets SQLite reuse the lock path stored in the conch. If opening that old path later fails for reasons other than `SQLITE_NOMEM`, the routine loops once with `forceNewLockPath` and generates a fresh automatic path with `proxyGetLockPath()`. For explicit proxy paths, both host id and path content must match to accept the existing conch record. When the conch must be changed, read-only conch descriptors fail with `SQLITE_BUSY`; writable conches take an exclusive conch lock, write the version/host/path record, truncate the file to the exact record length, and call `full_fsync()`. Newly created conch files attempt to inherit database read/write permission bits with `fchmod()`.

After conch validation or update, `proxyTakeConch()` reopens the database file using the original `pFile->openFlags`. It then opens the proxy lock file through `proxyCreateUnixFile()`, duplicates any stack/extracted path into `pCtx->lockProxyPath`, marks `conchHeld=1`, and patches AFP proxy contexts so `afpCtx->dbPath` points at the selected lock-proxy path. On failure it unlocks the conch to `NO_LOCK`.

`proxyTransformUnixFile()` is the activation path for proxy locking. It refuses to operate unless the file is unlocked, derives the database path from the current locking style, allocates a new proxy context, derives and opens the conch path, optionally enters lockless mode for read-only opens on read-only filesystems without a conch file, stores the database path, and finally swaps `pFile->pMethod` to `proxyIoMethods`. Any failure before the swap closes the conch file and frees the partially built context.

The proxy I/O methods are thin after conch acquisition. `proxyCheckReservedLock()` delegates to `lockProxy->pMethod->xCheckReservedLock()`. `proxyLock()` and `proxyUnlock()` delegate to the proxy lock file and then mirror `proxy->eFileLock` back into the database `unixFile`. In lockless mode (`conchHeld<0`), these methods do not acquire a proxy lock; `proxyCheckReservedLock()` intends to report no reserved lock.

`sqlite3_os_init()` defines the `UNIXVFS` macro locally, constructs the compiled-in VFS list, asserts that the syscall shim table has the expected size, and registers each VFS. The first VFS in the array becomes the default unless `SQLITE_DEFAULT_UNIX_VFS` names a matching entry. Optional KV VFS initialization runs after registration. The routine then allocates static mutex slots, validates WAL shared-memory lock offsets in non-`SQLITE_OMIT_WAL` builds, initializes the temp-directory list, and returns `SQLITE_OK`.

## State And Persistence Behavior

- Conch files persist beside the database with a transformed name such as `.database-conch`. Their content persists the proxy-lock format version, host id, and lock-proxy path.
- Proxy lock files persist separately, usually under the Darwin user temp directory or configured `LOCKPROXYDIR`, with database path characters transformed by the earlier `proxyGetLockPath()` helper and a `:auto:` suffix for automatic names.
- `proxyLockingContext` owns `conchFile`, `conchFilePath`, `lockProxy`, `lockProxyPath`, `dbPath`, `conchHeld`, the old locking context, and the old I/O methods. This context replaces the original `unixFile.lockingContext` until `proxyClose()` restores it.
- `pCtx->conchHeld` is tri-state in practice: `0` means not held, `1` means conch lock and proxy file are active, and `-1` means read-only filesystem lockless mode.
- `proxyTakeConch()` can close and reopen `pFile->h` to avoid stale descriptors after conch changes or lock-path selection.
- Conch updates are durable at the file level: the code truncates the conch, writes the exact payload through `unixWrite()`, and calls `full_fsync()`.
- When creating a conch file, the code tries to copy database user/group/other read-write permission bits to the conch file. Failures are ignored in non-debug builds.
- `sqlite3_os_init()` stores a static `aVfs[]` array whose `pNext` links are later modified by SQLite core registration. This is process-global registration state, not database-file state.
- `unixBigLock` and `vxworksMutex` are global static mutex pointers allocated during OS init and nulled during OS end. `sqlite3_os_end()` does not free filesystem artifacts.
- `unixTempFileInit()` initializes process-local temp-directory discovery state used by later Unix temp-file operations.

## Dependencies And Integration Points

- The whole proxy-locking block is compiled only for `defined(__APPLE__) && SQLITE_ENABLE_LOCKING_STYLE`, matching the comment that proxy locking is intended for AFP filesystems on macOS.
- Proxy locking depends on the surrounding `proxyLockingContext` definition and earlier helpers `proxyGetLockPath()`, `proxyCreateLockPath()`, and `proxyCreateUnixFile()`.
- The conch and proxy lock files are regular `unixFile` objects filled by `fillInUnixFile()` with a dummy VFS whose finder is `autolockIoFinder`, so their actual locking methods may be AFP, dotfile, flock, POSIX, or other compiled-in styles depending on filesystem detection.
- The proxy methods integrate with the `IOMETHODS()` macro earlier in the file, where `proxyIoMethods` is declared with `proxyClose`, `proxyLock`, `proxyUnlock`, and `proxyCheckReservedLock` and with shared-memory support disabled.
- `unixFileControl()` routes the proxy-specific `SQLITE_FCNTL_GET_LOCKPROXYFILE` and `SQLITE_FCNTL_SET_LOCKPROXYFILE` opcodes to `proxyFileControl()` for files using the proxy method or for activation requests.
- Lock constants `NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, and `EXCLUSIVE_LOCK` follow SQLite's common pager/VFS locking contract; proxy locking preserves the database file's visible `eFileLock` by mirroring the proxy lock file state.
- `proxyTakeConch()` uses low-level OS wrappers and SQLite helpers including `osPread`, `osPwrite`, `seekAndRead`, `robust_open`, `robust_close`, `robust_ftruncate`, `storeLastErrno`, `unixWrite`, `full_fsync`, `osFstat`, `osFchmod`, `osStat`, `futimes`, `statfs`, and `unixSleep`.
- `sqlite3_os_init()` integrates this file with SQLite core by calling `sqlite3_vfs_register()`. Its VFS method table points at Unix VFS entry points from earlier in the file: `unixOpen`, `unixDelete`, `unixAccess`, `unixFullPathname`, dynamic loader methods, randomness, sleep/time methods, last-error reporting, and syscall override APIs.
- Build flags determine VFS availability: Apple locking-style builds expose autolock, AFP, NFS, flock, and proxy variants; VxWorks exposes named semaphores and its own default finder; generic Unix uses POSIX by default plus no-lock, dotfile, exclusive, and sometimes explicit POSIX/flock names.
- Optional `SQLITE_OS_KV_OPTIONAL` integrates `sqlite3KvvfsInit()` into OS initialization.
- Non-`SQLITE_OMIT_WAL` builds rely on the asserted relationship among `SQLITE_SHM_NLOCK`, `UNIX_SHM_BASE`, and `UNIX_SHM_DMS` because WAL shared-memory locking uses fixed byte offsets.

## Risks And Edge Cases

- `proxyBreakConchLock()` assumes the conch path ends with a five-character `conch` suffix and rewrites the last five characters to `break`. Unexpected path shapes fail with a path error, but the logic is tightly coupled to `proxyCreateConchPathname()`.
- Stale conch breaking depends on filesystem modification timestamps and host-id equality. Coarse timestamp resolution, clock/filesystem anomalies, or host-id duplication could cause either false busy results or unsafe lock breaking.
- The conch format stores a path without an explicit trailing NUL in the on-disk record length. Readers cap the copied path and add a local NUL, but path comparison for explicit proxy paths uses `strncmp()` with `readLen-PROXY_PATHINDEX`, so malformed or prefix-like records deserve regression coverage.
- `proxyTakeConch()` calls `futimes(conchFile->h, NULL)` before exclusive locking so other contenders can observe modification-time movement. A failure is ignored, which may weaken stale-lock detection on filesystems where `futimes()` is unsupported or unreliable.
- If another thread in the same process holds a shared conch lock (`pInode->nShared>1`), upgrading to exclusive returns `SQLITE_BUSY`. This avoids self-deadlock but means same-process proxy-lock users can block path changes or conch rewrites.
- `proxyCreateUnixFile()` returns `SQLITE_BUSY` for lock-file open failures after read-write and read-only attempts. `proxyTakeConch()` only retries automatic path generation for old conch paths and non-`SQLITE_NOMEM` failures, so persistent permission/path problems may surface as busy rather than cantopen.
- The lockless read-only filesystem path sets `conchHeld=-1`. In this mode proxy `xLock` and `xUnlock` become no-ops, which is only safe for genuinely read-only database access on read-only media.
- In `proxyCheckReservedLock()`, the lockless branch assigns `pResOut=0` instead of `*pResOut=0`. That statement only changes the local pointer variable and leaves the caller's output untouched, so lockless reserved-lock checks depend on caller initialization or are a latent bug signal.
- `switchLockProxyPath()` can allocate `lockProxyPath` with `sqlite3DbStrDup()` without checking for NULL before returning `SQLITE_OK`. Later conch acquisition may fail or behave as `:auto:` if allocation failed.
- `proxyClose()` returns immediately on unlock/close errors before freeing later resources or restoring original methods. This preserves error reporting but can leave cleanup incomplete if lower-level close operations fail.
- `proxyFileControl()` rejects turning off proxy locking once enabled. Callers that expect `SQLITE_FCNTL_SET_LOCKPROXYFILE` with NULL to disable proxy locking will receive `SQLITE_ERROR`.
- The static assertion `ArraySize(aSyscall)==29` is a maintenance tripwire: adding or removing syscall shim entries elsewhere requires updating this expected count.
- VFS default selection depends on compile-time flags and registration order. Changing `aVfs[]` order or `SQLITE_DEFAULT_UNIX_VFS` handling can alter the default locking behavior for all Unix opens.
- WAL offset assertions are not runtime compatibility negotiation. If constants drift, debug builds fail early; release builds still rely on the same fixed layout.

## Test Signals

- Apple locking-style builds should exercise `unix-proxy` open, close, shared/reserved/exclusive lock transitions, unlock transitions, and reserved-lock checks with a real or mocked proxy lock file.
- `SQLITE_FCNTL_SET_LOCKPROXYFILE` should be covered for activating proxy locking on an unlocked file, switching to a new explicit path while unlocked, no-op behavior for `:auto:` and matching paths, `SQLITE_BUSY` when switching while locked, and `SQLITE_ERROR` when trying to disable proxy locking after activation.
- `SQLITE_FCNTL_GET_LOCKPROXYFILE` should return NULL for non-proxy files, `:auto: (not held)` before an automatic conch path is resolved, and the resolved `lockProxyPath` after conch acquisition.
- Conch-format tests should cover new conch creation, valid host/path reuse, short reads, wrong version bytes, mismatched host ids, explicit path mismatches, and automatic path fallback when a stale conch path cannot be opened.
- Stale-lock tests should simulate repeated `SQLITE_BUSY`, stable and changing conch modification times, matching and mismatching host ids, and successful/failed `proxyBreakConchLock()` rename paths.
- Permission tests should verify that newly created conch files try to inherit database read/write permission bits and that failure to chmod does not abort normal non-debug operation.
- Read-only filesystem tests should cover the branch where the conch does not exist, the database is opened read-only, `statfs()` reports `MNT_RDONLY`, and proxy locking enters `conchHeld=-1` lockless mode.
- OOM and allocation-failure tests should target `proxyCreateConchPathname()`, `proxyTransformUnixFile()`, `sqlite3DbStrDup()` of proxy/database paths, and `proxyCreateUnixFile()` allocation of `unixFile` and `UnixUnusedFd`.
- Close-error tests should verify how proxy resources behave if unlocking or closing the proxy lock file or conch file fails.
- VFS registration tests should verify compiled-in VFS name availability for generic Unix, VxWorks, and Apple locking-style configurations, and that `SQLITE_DEFAULT_UNIX_VFS` selects the named default when configured.
- Initialization tests should run with WAL enabled to hit the shared-memory offset assertions in debug builds, and with `SQLITE_OS_KV_OPTIONAL` to ensure KV VFS initialization still composes with Unix VFS registration.
