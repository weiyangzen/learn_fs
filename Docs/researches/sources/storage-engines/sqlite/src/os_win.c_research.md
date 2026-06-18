# sources/storage-engines/sqlite/src/os_win.c

## Purpose

`os_win.c` is SQLite's Windows-only VFS and file I/O backend. It is compiled only when `SQLITE_OS_WIN` is true and implements the `sqlite3_vfs` and `sqlite3_io_methods` contracts for native Windows, UWP/WinRT variants, and Cygwin-on-Windows builds. The file translates SQLite's portable storage operations into Win32 file handles, byte-range locks, wide-character paths, shared-memory mappings, memory-mapped database reads, temporary-file naming, randomness/time services, extension loading, and optional Win32 heap allocation.

The module registers four VFS names at `sqlite3_os_init()`: `win32`, `win32-longpath`, `win32-none`, and `win32-longpath-none`. The `none` variants use the same file I/O implementation but replace lock methods with no-op locking for externally synchronized or read-only use cases. The long-path variants raise `mxPathname` from the normal Win32 path limit to the NT Unicode path limit.

## Important APIs, Types, And Functions

- `struct winFile` subclasses `sqlite3_file`. It stores the active `sqlite3_io_methods`, owning VFS, Windows `HANDLE`, current SQLite lock state, readonly/persistent-WAL/powersafe-overwrite bits, last Win32 error, database path, chunk-size hint, optional WAL shared-memory object, optional mmap state, and optional blocking-lock timeout state.
- `struct winVfsAppData` is attached to each registered VFS and selects either the normal or no-lock `sqlite3_io_methods` vector.
- `aSyscall[]`, `winSetSystemCall()`, `winGetSystemCall()`, and `winNextSystemCall()` wrap Win32 and Cygwin system calls behind overrideable function pointers. SQLite tests and embedders can inject failures or sandbox implementations through the VFS `xSetSystemCall` family.
- Optional `SQLITE_WIN32_MALLOC` code exposes a `sqlite3_mem_methods` implementation backed by `HeapCreate`, `HeapAlloc`, `HeapReAlloc`, `HeapFree`, `HeapSize`, and `HeapDestroy`. Public helpers include `sqlite3_win32_compact_heap()` and `sqlite3_win32_reset_heap()`.
- Public conversion/directory helpers include `sqlite3_win32_utf8_to_unicode()`, `sqlite3_win32_unicode_to_utf8()`, `sqlite3_win32_mbcs_to_utf8()`, `sqlite3_win32_utf8_to_mbcs()`, `sqlite3_win32_set_directory8()`, `sqlite3_win32_set_directory16()`, and `sqlite3_win32_set_directory()`.
- Core file methods are `winClose()`, `winRead()`, `winWrite()`, `winTruncate()`, `winSync()`, `winFileSize()`, `winLock()`, `winUnlock()`, `winCheckReservedLock()`, `winFileControl()`, `winSectorSize()`, `winDeviceCharacteristics()`, `winFetch()`, and `winUnfetch()`.
- WAL/shared-memory methods are `winShmMap()`, `winShmLock()`, `winShmBarrier()`, and `winShmUnmap()`, backed by `winOpenSharedMemory()`, `winCloseSharedMemory()`, `winShmPurge()`, `winLockSharedMemory()`, and the `winShmNode`/`winShm` object graph.
- VFS methods are `winOpen()`, `winDelete()`, `winAccess()`, `winFullPathname()`, `winDlOpen()`, `winDlError()`, `winDlSym()`, `winDlClose()`, `winRandomness()`, `winSleep()`, `winCurrentTime()`, `winCurrentTimeInt64()`, and `winGetLastError()`.
- Path helpers include `winConvertFromUtf8Filename()`, `winIsDir()`, `winIsLongPathPrefix()`, `winIsDriveLetterAndColon()`, `winIsVerbatimPathname()`, Cygwin-only `winSimplifyName()`/`mkFullPathname()`, `winMakeEndInDirSep()`, and `winGetTempname()`.
- Lock helpers include `winLockFile()`, `winUnlockFile()`, `winGetReadLock()`, `winUnlockReadLock()`, `winHandleLockTimeout()`, and `winHandleUnlock()`.

## Control Flow

`sqlite3_os_init()` is the module entry point. It asserts the syscall table layout, calls `GetSystemInfo()` to capture page size and allocation granularity for mmap alignment, registers the four Windows VFS objects, and initializes `winBigLock` for WAL shared-memory bookkeeping when WAL is enabled. `sqlite3_os_end()` only clears the WAL global lock pointer.

Opening a file flows through `winOpen()`. It validates SQLite open flags, generates a temp name if `zName` is null, converts the UTF-8 path to a Windows wide path, rejects directories, maps SQLite flags to `CreateFileW()` access/share/create/disposition attributes, retries transient sharing/locking errors, and falls back from read-write to read-only when a read-only file is detected and exclusive-create is not required. On success it fills `winFile`, installs either normal or no-lock I/O methods from `pVfs->pAppData`, records readonly and powersafe-overwrite flags, initializes mmap limits, and increments the open counter.

Read and write paths use explicit offsets. With overlapped I/O enabled, `winRead()` and `winWrite()` populate an `OVERLAPPED` structure rather than mutating the handle file pointer. If `SQLITE_WIN32_NO_OVERLAPPED` is set, they seek first with `winSeekFile()`. Reads can be satisfied partly or fully from `pMapRegion`; short reads are zero-filled and returned as `SQLITE_IOERR_SHORT_READ`. Writes loop until all bytes are written, retrying transient Win32 errors and distinguishing disk-full errors as `SQLITE_FULL`.

SQLite lock state is implemented with Windows byte-range locks. `winLock()` only raises the lock level and follows SQLite's lock ladder: `NO_LOCK -> SHARED_LOCK`, `SHARED_LOCK -> RESERVED_LOCK`, and `SHARED/RESERVED -> PENDING -> EXCLUSIVE`. It uses `PENDING_BYTE`, `RESERVED_BYTE`, and the `SHARED_FIRST..SHARED_SIZE` range. `winUnlock()` releases exclusive/shared/reserved/pending byte ranges as needed and can downgrade only to `SHARED_LOCK` or `NO_LOCK`. `winCheckReservedLock()` probes the reserved byte unless the local file already holds a reserved-or-stronger lock. The no-lock VFS uses `winNolockLock()`, `winNolockUnlock()`, and `winNolockCheckReservedLock()`.

`winFileControl()` is the bridge for runtime controls. It exposes lock state, last errno, chunk-size and size-hint preallocation, persistent-WAL and powersafe-overwrite flags, VFS name reporting, AV retry tuning, raw Win32 handle access, temp filename creation, mmap-size updates, blocking-lock timeout, block-on-connect behavior, null-I/O testing, and optional JSON file statistics.

The WAL path lazily opens shared memory from `winShmMap()`. `winOpenSharedMemory()` creates or finds a process-wide `winShmNode` for `dbpath-shm`, opens a shared mapping handle, creates a per-node mutex, and links a per-connection `winShm`. A deadman-switch byte (`WIN_SHM_DMS`) detects first opener and truncates stale `-shm` content before taking a shared DMS lock. `winShmMap()` grows and maps region arrays with `CreateFileMappingW()`/`MapViewOfFile()` or UWP equivalents. `winShmLock()` tracks per-connection shared and exclusive lock masks and applies byte-range locks at `WIN_SHM_BASE + ofst`, with special same-process handling for UNC paths that must use a shared lock handle.

Path handling converts SQLite's UTF-8 names to Windows `WCHAR` names. Native Windows builds mainly use `winUtf8ToUnicode()` and `GetFullPathNameW()`. Cygwin builds can call `cygwin_conv_path()`, preserve or synthesize `\\?\`/`\\?\UNC` prefixes for long names, resolve symlinks up to `SQLITE_MAX_SYMLINKS`, and normalize separators. `winFullPathname()` serializes full-path computation with the temp-directory mutex because it may inspect `sqlite3_data_directory`.

Mmap support is opportunistic. `winMapfile()` maps up to the configured mmap limit and logs mapping errors while continuing with normal `xRead`/`xWrite`. `winFetch()` returns pointers only when the requested range plus a 256-byte safety buffer fits inside the mapping, and increments `nFetchOut`; `winUnfetch()` decrements outstanding fetches or unmaps the whole file when called with a null pointer.

## State And Persistence Behavior

Persistent database state reaches disk through Win32 file handles, file mappings, and byte-range locks. `winWrite()` persists data through `WriteFile()` and `winSync()` flushes both mapped views (`FlushViewOfFile()`) and file handles (`FlushFileBuffers()`) unless `SQLITE_NO_SYNC` is compiled. `winTruncate()` can round requested sizes up to the configured chunk size and remaps the file afterward if a previous mapping existed.

Lock state is persisted in OS file-lock tables and mirrored in `winFile.locktype`. WAL shared-memory state is stored in the `-shm` file, mapped into process memory by `winShmNode.aRegion`, and coordinated with byte locks. Per-process bookkeeping is held in the global `winShmNodeList`, protected by `winBigLock`; per-node connection lists and region arrays are protected by each node mutex.

The module stores mutable process-global knobs. `winIoerrRetry` and `winIoerrRetryDelay` can be changed via `SQLITE_FCNTL_WIN32_AV_RETRY`. `sqlite3_temp_directory` and `sqlite3_data_directory` are set via public Win32 directory APIs. Optional test globals include `sqlite3_os_type`, `sqlite3_sync_count`, `sqlite3_fullsync_count`, `sqlite3_current_time`, and `sqlite3_win_test_unc_locking`.

Temporary-file names are generated under `sqlite3_temp_directory` when set, otherwise from Cygwin environment candidates or `GetTempPathW()`. Names use SQLite's temp prefix plus 15 pseudo-random alphanumeric bytes mixed with the process id. Delete-on-close files use `FILE_ATTRIBUTE_TEMPORARY`, `FILE_ATTRIBUTE_HIDDEN`, and `FILE_FLAG_DELETE_ON_CLOSE`.

The optional Win32 heap backend is process-global through `win_mem_data`. When it owns an isolated heap, `winMemShutdown()` destroys all allocations on shutdown; `sqlite3_win32_reset_heap()` will only destroy and recreate that heap while the main and memory mutexes are held and `sqlite3_memory_used()` is zero.

## Dependencies And Integration Points

This file depends on SQLite internals from `sqliteInt.h` and common OS-layer helpers from `os_common.h`. It implements the low-level callbacks consumed by the pager, WAL, temp-store, extension loader, randomness, date/time, and mutex/thread subsystems.

Major Windows APIs include `CreateFileW`, `ReadFile`, `WriteFile`, `SetFilePointerEx`, `SetEndOfFile`, `GetFileSizeEx`, `FlushFileBuffers`, `LockFileEx`, `UnlockFileEx`, `CreateFileMappingW`, `MapViewOfFile`, `UnmapViewOfFile`, `GetFileAttributesExW`, `DeleteFileW`, `GetFullPathNameW`, `GetTempPathW`, `FormatMessageW`, `LoadLibraryW`, `GetProcAddress`, `FreeLibrary`, `GetSystemTimeAsFileTime`, `GetTickCount64`, `QueryPerformanceCounter`, `Sleep`, `WaitForSingleObjectEx`, and optional RPC UUID and heap APIs. UWP builds use `CreateFileMappingFromApp()` and `MapViewOfFileFromApp()` where required. Cygwin builds integrate with `getenv`, `getcwd`, `lstat`, `readlink`, `errno`, and `cygwin_conv_path()`.

Internal callers and consumers visible in nearby source include `threads.c` (`sqlite3Win32Wait()`), `mutex_w32.c` (`sqlite3_win32_sleep()`), `shell.c.in` (UTF-8/UTF-16 conversion helpers), `test1.c` (Win32 file-control test commands), `sqlite.h.in` (public Win32 directory and file-control declarations), and `wal.c` (shared-memory lock offset expectations).

The VFS depends on SQLite compile-time options. `SQLITE_OMIT_WAL`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_MMAP_READWRITE`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_UWP`, `__CYGWIN__`, `SQLITE_WIN32_MALLOC`, `SQLITE_ENABLE_SETLK_TIMEOUT`, `SQLITE_TEST`, `SQLITE_NO_SYNC`, and `SQLITE_ENABLE_API_ARMOR` materially alter exported helpers, methods, locking behavior, and error paths.

## Risks And Edge Cases

- Windows sharing and antivirus/indexer interference are first-class risks. The file retries selected `GetLastError()` values for reads, writes, deletes, opens, directory checks, and access checks, but retry behavior is globally mutable and must not mask real errors indefinitely.
- Lock sequencing is fragile. Incorrect changes to pending/reserved/shared byte ranges, local `locktype`, or SHM masks can corrupt rollback-journal or WAL concurrency. The no-lock VFS is explicitly unsafe for concurrent writers unless an external lock exists.
- Mmap has correctness constraints around outstanding fetches. `winTruncate()` intentionally becomes a no-op when `nFetchOut>0`, which can leave database files larger than expected but avoids invalidating active mapped pointers.
- Path conversion spans UTF-8, UTF-16, MBCS, Win32 long paths, UNC paths, verbatim paths, data directories, temp directories, and Cygwin POSIX paths. Small separator or prefix changes can break long-path, URI, UNC, or symlink behavior.
- WAL shared-memory cleanup is shared-process state. `winShmPurge()` must unmap all regions, close mapping handles, close the shared `-shm` handle, optionally delete the file, and remove only nodes with no connection list.
- UWP and omitted-feature builds leave some syscall pointers null by design. Callers must respect compile-time guards before invoking load-extension, heap, mmap, or temp-path APIs unavailable on those targets.
- `winGetLastErrorMsg()` depends on `FormatMessageW()` allocation and UTF-8 conversion. It uses benign malloc handling but still must tolerate conversion failure while logging I/O errors.
- `SQLITE_WIN32_MALLOC` isolated heaps are dangerous after shutdown: destroying the heap invalidates all outstanding allocations immediately.
- `winRandomness()` mixes time, pid, tick count, performance counter, and optionally UUIDs. It is platform entropy gathering, not a cryptographic RNG by itself, and test/omit-randomness builds deliberately return zero-filled bytes.
- `SQLITE_FCNTL_WIN32_GET_HANDLE` exposes the raw file handle to embedders. Misuse outside SQLite can violate assumptions about handle lifetime, offset, locks, or mappings.

## Test Signals

Existing repository signals include `test/win32longpath.test` for the `win32-longpath` VFS; `test1.c` helpers for `SQLITE_FCNTL_WIN32_AV_RETRY`, `SQLITE_FCNTL_WIN32_GET_HANDLE`, and `SQLITE_FCNTL_WIN32_SET_HANDLE`; `mutex_w32.c` and `threads.c` integration with Win32 sleep/wait helpers; and shell code using UTF-8/UTF-16 conversion wrappers.

High-value tests should cover:

- VFS registration and selection of `win32`, `win32-longpath`, `win32-none`, and `win32-longpath-none`.
- Open modes for main DB, journals, WAL files, temp DBs, delete-on-close files, exclusive create, read-only fallback, URI `exclusive`, URI `psow`, and directory rejection.
- Lock transitions through SHARED, RESERVED, PENDING, and EXCLUSIVE, including downgrade behavior, reserved-lock probing, readonly write-lock refusal, blocking-lock timeout, and UNC shared-handle SHM locking.
- WAL region lifecycle: first-opener DMS truncation, readonly `-shm`, region growth, map/unmap cleanup, shared/exclusive SHM lock masks, and delete-on-unmap behavior.
- Mmap fetch/unfetch behavior, mapping failures falling back to normal I/O, truncation with outstanding fetch references, mmap-size file control, and read/write through mapped regions when enabled.
- Retry behavior for `ERROR_ACCESS_DENIED`, `ERROR_SHARING_VIOLATION`, `ERROR_LOCK_VIOLATION`, network errors, and disk-full errors.
- Long-path, UNC, verbatim, data-directory, temp-directory, Cygwin POSIX path, drive-relative, symlink, and separator normalization cases.
- Public conversion APIs and directory setters under normal, null-argument API-armor, MBCS ANSI/OEM, and autoinit-failure conditions.
- Extension loading success/failure and UWP or `SQLITE_OMIT_LOAD_EXTENSION` disabled cases.
- Time/randomness outputs, `SQLITE_TEST` fake time, sync counters, `SQLITE_NO_SYNC`, and error-message formatting.
- Optional Win32 heap allocation, compaction, reset, validation failure handling, shutdown behavior, and process-heap versus isolated-heap modes.
