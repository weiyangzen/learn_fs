# sources/storage-engines/sqlite/ext/wasm/api/opfs-common-shared.c-pp.js

## Purpose

This browser-only initializer builds the internal `sqlite3.opfs` namespace shared by the `opfs` and `opfs-wl` VFS implementations. It supplies OPFS feature detection, utility filesystem operations, database import helpers, VFS option normalization, and the common synchronous-to-async bridge used to expose SQLite's synchronous VFS methods on top of OPFS APIs and a worker proxy.

## Important APIs and control flow

The initializer exits if OPFS VFS installation is disabled. It then creates `sqlite3.opfs` with utilities such as `thisThreadHasOPFS()`, `getRootDir()`, `getResolvedPath()`, `getDirForFilename()`, `mkdir()`, `entryExists()`, `randomFilename()`, `treeList()`, `rmfr()`, `unlink()`, and `traverse()`. `importDb()` writes a verified SQLite database image into OPFS, either from a byte array or from async chunks, truncating the target first and rewriting header bytes 18 and 19 to force rollback-journal mode instead of WAL.

`vfsInstallationFeatureCheck(vfsName)` enforces `SharedArrayBuffer`, `Atomics`, worker context, OPFS sync access handles, and `Atomics.waitAsync()` for `opfs-wl`. `initOptions(vfsName, options)` reads URL flags, sets verbosity and sanity-check options, derives the async proxy URI, and returns a normalized options object or falsy when installation should be skipped.

`createVfsState()` builds the central VFS state. It constructs `capi.sqlite3_vfs` and `capi.sqlite3_io_methods`, allocates the VFS name, creates metrics, shared file and serialization buffers, operation IDs, exported SQLite result/open/lock constants for the async proxy, and OPFS-specific flags. `opfsVfs.opRun(op, ...args)` serializes arguments, writes an operation ID into a shared Int32 buffer, notifies the async worker, blocks with `Atomics.wait()` until a result appears, logs serialized exceptions, and returns the SQLite result code.

The synchronous IO wrappers implement `xClose`, `xFileSize`, `xRead`, `xSync`, `xTruncate`, and `xWrite`; VFS wrappers implement `xAccess`, time methods, `xDelete`, `xFullPathname`, `xGetLastError`, and `xOpen`. `xOpen` parses URI flags such as `opfs-unlock-asap=1` and `delete-before-open=1`, allocates per-file tracking, forwards open to the async side, installs `sqlite3_file` methods, and records open files. `bindVfs(ioMethods, callback)` merges VFS-specific methods, starts `sqlite3-opfs-async-proxy.js`, transfers cloneable state, handles worker init messages, installs the VFS through `sqlite3.vfs.installVfs`, initializes serialization, optionally runs sanity checks, and resolves to `sqlite3`.

## State, persistence, dependencies, and risks

Persistent state lives in the browser origin's OPFS tree. The VFS bridge state itself is volatile: `SharedArrayBuffer` instances hold file I/O buffers, serialized arguments, return codes, and operation notifications; `__openFiles` maps SQLite file pointers to per-file metadata; metrics counters track operation time and wait time. `importDb()` directly persists bytes to OPFS and deletes partial files on many errors.

Dependencies include browser OPFS APIs, worker execution, cross-origin isolation for `SharedArrayBuffer`, `Atomics.wait()`, the async proxy script, `sqlite3.capi`, `sqlite3.wasm`, `sqlite3.vfs.installVfs`, and the inline serializer. Key risks are environment gating failures, worker script resolution/404 timeouts, deadlocks or spurious wakeups in wait/notify handling, stale file-pointer bookkeeping, lock contention across tabs, partial import cleanup, and undefined behavior when deleting files used by another instance. Test signals include feature-check outcomes, byte-for-byte import plus WAL-mode header rewrite, `treeList/traverse/unlink` behavior, VFS install success, the optional sanity test's access/open/sync/truncate/write/read/close/delete sequence, metrics dumps, and multi-tab lock-contention tests for both `opfs` and `opfs-wl`.
