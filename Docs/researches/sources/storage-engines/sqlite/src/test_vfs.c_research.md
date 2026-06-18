# sources/storage-engines/sqlite/src/test_vfs.c

## Purpose

`test_vfs.c` implements the Tcl `testvfs` command used by SQLite tests to create instrumented VFS wrappers. A test VFS forwards real file I/O to a parent VFS while invoking Tcl callbacks, injecting I/O/full/cantopen faults, overriding device characteristics and sector size, and optionally replacing WAL shared-memory methods with an in-memory model. It is compiled only under `SQLITE_TEST`.

## Important APIs, Types, And Functions

- `Testvfs` stores the registered VFS, parent VFS, Tcl interpreter/script, callback mask, SHM buffers, fault injectors, device flags, and sector size.
- `TestvfsFile` is the public `sqlite3_file` wrapper; `TestvfsFd` stores the parent real file, filename, SHM id, SHM buffer link, and local SHM lock masks.
- `TestvfsBuffer` stores per-database in-memory SHM pages shared by all handles opened through the test VFS.
- `TestFaultInject` and `tvfsInjectFault()` implement transient or persistent fault countdowns.
- `tvfs_io_methods` provides xClose, xRead, xWrite, xTruncate, xSync, xFileSize, locks, file-control, SHM, fetch, and unfetch wrappers.
- `tvfsOpen()`, `tvfsDelete()`, `tvfsAccess()`, `tvfsFullPathname()`, `tvfsRandomness()`, `tvfsSleep()`, and `tvfsCurrentTime()` implement `sqlite3_vfs` methods.
- `tvfsShmOpen()`, `tvfsShmMap()`, `tvfsShmLock()`, `tvfsShmBarrier()`, and `tvfsShmUnmap()` implement the in-memory SHM backend unless `-fullshm` forwards to the parent VFS or `-noshm` removes SHM methods.
- `testvfs_obj_cmd()` implements object subcommands: `shm`, `delete`, `filter`, `ioerr`, `fullerr`, `cantopenerr`, `script`, `devchar`, and `sectorsize`.
- `testvfs_cmd()` creates and registers a named VFS plus a Tcl object command of the same name.
- `vfs_shmlock` and `vfs_set_readmark` are direct Tcl helpers for WAL SHM locking and readmark mutation.

## Control Flow

`Sqlitetestvfs_Init()` registers `testvfs`, `vfs_shmlock`, and `vfs_set_readmark`. `testvfs VFSNAME ?options?` parses options such as `-noshm`, `-fullshm`, `-default`, `-szosfile`, `-mxpathname`, and `-iversion`, creates a `Testvfs` object, captures the current default VFS as its parent, installs a Tcl object command, fills a copy of the static `sqlite3_vfs`, and registers it with SQLite.

Every file open allocates a `TestvfsFd` followed by parent `szOsFile` bytes for the real file. `tvfsOpen()` optionally invokes the Tcl script as `xOpen`, supports result-code override or connection id naming, injects configured faults, opens the real file through the parent VFS, then installs a copy of `tvfs_io_methods` trimmed to the configured VFS version and SHM policy.

Most I/O methods follow the same pattern: if a script is installed and the method bit is enabled, call `tvfsExecTcl()` with method-specific arguments; interpret symbolic result strings with `tvfsResultCode()`; apply configured fault injection when appropriate; and delegate to `sqlite3Os*` on the real file. `xWrite` treats a negative Tcl result-code mapping as "skip real write but return OK", which supports tests that simulate lost writes.

The default SHM model is process-local. `tvfsShmOpen()` finds or creates a `TestvfsBuffer` by full filename and links each open handle into it. `tvfsShmMap()` lazily opens SHM, optionally invokes callbacks and faults, allocates pages on write, and returns pointers from `aPage`. `tvfsShmLock()` checks the linked handle list for conflicting exclusive/shared masks and updates per-handle masks. `tvfsShmUnmap()` unlinks the handle and frees all pages when the last handle closes.

The object command controls runtime behavior. `filter` selects which VFS methods trigger scripts and I/O faults. `script` sets the Tcl callback prefix. `ioerr`, `fullerr`, and `cantopenerr` arm countdown-based faults and return the previous failure count. `shm` reads or replaces in-memory SHM content. `devchar` and `sectorsize` override values returned by xDeviceCharacteristics and xSectorSize.

## State And Persistence Behavior

Real database, journal, WAL, and temp-file persistence remains delegated to the parent VFS unless a Tcl callback or fault changes behavior. In-memory SHM state in the default test model is not persisted to `-shm` files; it lives in `TestvfsBuffer` pages and is shared only within the test process and VFS object.

Fault injector state is mutable per `Testvfs`: `iCnt` counts down, persistent faults continue after the first failure, and `nFail` is returned and reset when the Tcl subcommand is queried. Callback filters and scripts are per VFS object. File objects own Tcl reference-counted SHM ids and copied method tables. Deleting the object command unregisters the VFS and frees object state.

## Dependencies And Integration Points

The module depends on SQLite's public VFS and I/O-method contracts, internal `sqlite3Os*` wrappers, Tcl command/object APIs, and testfixture helpers `getDbPointer()` and `sqlite3ErrName()`. It exercises pager, WAL, atomic-write, file-control, mmap fetch/unfetch, device capability, and VFS registration paths.

The Tcl script callback protocol is an integration surface for many SQLite tests. Callback method names include `xOpen`, `xClose`, `xRead`, `xWrite`, `xSync`, `xDelete`, `xAccess`, `xFullPathname`, `xLock`, `xUnlock`, `xCheckReservedLock`, `xFileControl`, `xSleep`, and SHM methods.

## Risks And Edge Cases

- The in-memory SHM model is a testing approximation, not an OS-level interprocess SHM implementation. It cannot test cross-process locking semantics.
- `TESTVFS_MAX_PAGES` caps SHM pages at 1024; out-of-range page requests rely on assertions in debug builds.
- Callback scripts run in the stored interpreter and can return result codes that alter VFS behavior; malformed or unexpected results fall back to parent behavior in several paths.
- `tvfsExecTcl()` increments the script object's refcount but does not decrement the duplicate evaluation object directly, so Tcl lifetime assumptions are important.
- Full SHM forwarding, no-SHM trimming, and VFS `iVersion` trimming change method availability and must match SQLite's VFS ABI expectations.
- Fault injection is method-mask-sensitive for many methods but not all fault types; tests must configure `filter` deliberately.
- `tvfsClose()` closes the parent file and frees wrapper state even if callbacks fail, so callback errors become background Tcl errors rather than SQLite close failures.
- `devchar` stores an internal marker bit while returning named flags, which can surprise direct numeric inspection.

## Test Signals

Tests should verify VFS creation/deletion, default VFS registration, option parsing, method filtering, callback argument shapes, symbolic result-code overrides, transient and persistent `ioerr/fullerr/cantopenerr` behavior, `xWrite` skip semantics, SHM map/lock/unmap behavior, `-noshm` and `-fullshm` modes, device characteristic and sector-size overrides, file-control pragma hooks, mmap fetch forwarding, `vfs_shmlock`, and `vfs_set_readmark`.
