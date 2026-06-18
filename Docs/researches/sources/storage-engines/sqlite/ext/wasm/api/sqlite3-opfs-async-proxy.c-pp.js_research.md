# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-opfs-async-proxy.c-pp.js

## Purpose
This file is the Worker-side asynchronous proxy for SQLite's OPFS VFS implementations (`opfs` and `opfs-wl`). The synchronous SQLite/WASM VFS half cannot directly await browser OPFS operations, so it communicates with this Worker using `postMessage`, `SharedArrayBuffer`, serialized arguments, and `Atomics`. The proxy translates SQLite VFS-style operations into Origin Private File System directory/file/sync-access-handle calls and reports SQLite result codes back through shared memory.

## Important APIs, Types, and Functions
The script expects a `vfs` URL parameter (`opfs` or `opfs-wl`) and posts availability/load/init messages such as `opfs-unavailable`, `opfs-async-loaded`, and `opfs-async-inited`. `installAsyncProxy()` owns setup after feature detection. `state` is populated by an `opfs-async-init` message and carries SQLite result codes, operation IDs, OPFS flags, shared buffers, serializer state, verbosity, idle wait timing, and root OPFS directory handle.

Key helpers include `getResolvedPath()`, `getDirForFilename()`, `closeSyncHandle()`, `closeSyncHandleNoThrow()`, `releaseImplicitLocks()`, `releaseImplicitLock()`, `getSyncHandle()`, `storeAndNotify()`, and `affirmNotRO()`. `GetSyncHandleError` wraps browser errors from `createSyncAccessHandle()` and `convertRc()` maps lock/not-found failures to SQLite codes such as `SQLITE_BUSY` or `SQLITE_CANTOPEN`.

`vfsAsyncImpls` implements the proxied operations: `opfs-async-shutdown`, `mkdir`, `xAccess`, `xClose`, `xDelete`, `xDeleteNoWait`, `xFileSize`, `xOpen`, `xRead`, `xSync`, `xTruncate`, `xWrite`, and VFS-specific `xLock`/`xUnlock` variants. The `opfs-wl` path uses `navigator.locks` Web Locks plus sync access handles; the legacy `opfs` path uses sync access handle ownership as the lock.

## Control Flow
At load time the script validates that it is not on the main thread and that `SharedArrayBuffer`, `Atomics`, OPFS handles, and `createSyncAccessHandle()` are available. `opfs-wl` additionally requires `Atomics.waitAsync`. If requirements are met, `navigator.storage.getDirectory()` resolves the OPFS root, the Worker posts `opfs-async-loaded`, and `onmessage` waits for `opfs-async-init`.

Initialization copies sync-side options into `state`, constructs typed views over `sabOP` and `sabIO`, validates that every async implementation has an operation ID, initializes the shared serializer from `opfs-common-inline.c-pp.js`, posts `opfs-async-inited`, and starts `waitLoop()`. `waitLoop()` waits for a non-zero operation ID in the shared op slot, clears it, deserializes arguments, dispatches to the corresponding async handler, and each handler eventually calls `storeAndNotify()` to place the SQLite result code in the shared `rc` slot and wake the synchronous side.

File operations look up metadata in `__openFiles` by opaque sqlite3_file pointer IDs. `xOpen` resolves/creates directories, optionally unlinks before open, creates a file handle, records read-only/delete-on-close/unlock policy metadata, and stores it by fid. `xRead` and `xWrite` move bytes through the shared file buffer view. Size, truncate, sync, and close operations use or release sync access handles as required. Idle waits release implicit locks to reduce cross-tab contention.

## State and Persistence Behavior
The real persistent data lives in OPFS. Worker state tracks open handles in `__openFiles`, implicit lock fids in `__implicitLocks`, and for Web Locks builds active locks in `__activeWebLocks`. Each open file record stores the absolute path, directory handle, file handle, shared byte buffer view, read-only flag, delete-on-close flag, current sync handle, and lock metadata.

Sync access handles are acquired lazily by `getSyncHandle()`. If an operation acquires a handle without an explicit SQLite lock, the fid is marked as implicitly locked and can be released during idle time or immediately when `OPFS_UNLOCK_ASAP` is active. Explicit Web Lock mode keeps the invariant that a held Web Lock also has a held sync access handle. `xClose` deletes files marked `SQLITE_OPEN_DELETEONCLOSE`, and `xDeleteNoWait` can recursively remove empty parent directories when invoked with the special sync flag `0x1234`.

## Dependencies and Integration Points
This Worker is not a public API and does not load SQLite JS/WASM directly. It relies on the synchronous OPFS VFS half (`sqlite3-vfs-opfs.js` style generated code) to provide shared buffers, operation IDs, SQLite constants, OPFS flags, serialized arguments, and retry/idle settings. It includes `opfs-common-inline.c-pp.js` under an `opfs-async-proxy` define for shared serialization logic.

Browser dependencies are strong: Worker context, OPFS (`navigator.storage.getDirectory` and file/directory handles), `FileSystemFileHandle.prototype.createSyncAccessHandle`, `SharedArrayBuffer`, `Atomics`, and optionally `Atomics.waitAsync`/`navigator.locks` for `opfs-wl`. Deployments need cross-origin isolation headers for shared memory.

## Risks and Edge Cases
The proxy is timing-sensitive. It relies on Atomics slots being cleared and notified in the right order; spurious wakeups are explicitly handled. OPFS sync access handle acquisition can fail due to cross-tab locks, deletion races, or browser-specific exception names. The retry loop maps known lock errors to `SQLITE_BUSY`, but some browser failures fall back to generic I/O codes.

Implicit lock retention improves benchmark performance but can worsen concurrency; `OPFS_UNLOCK_ASAP` trades performance for earlier release. Web Lock upgrades from shared to exclusive are not atomic, and the code carefully releases/reacquires to avoid deadlocks. `xAccess` cannot fully model SQLite xAccess semantics because OPFS lacks read-only and cheap lock-state checks. `Number(offset64)` and `Number(sz)` conversions assume offsets/sizes are within JS safe numeric range for practical OPFS use.

Shutdown/restart exists mainly for debugging. A fatal exception inside `waitLoop()` is logged but does not necessarily notify the synchronous side for the failed operation unless the handler already serialized a result.

## Test Signals
Coverage should include feature-detection failure messages, successful `opfs-async-init`, mkdir and nested xOpen creation, unlink-before-open, read short-fill behavior, write/truncate/sync/read-only failures, delete-on-close, recursive cleanup flag, implicit lock release timing, contention mapping to `SQLITE_BUSY`, NotFound mapping during handle acquisition, legacy `opfs` lock/unlock, Web Locks shared/exclusive/downgrade paths for `opfs-wl`, operation dispatch with both `Atomics.wait` and `Atomics.waitAsync`, and browser deployment with required COOP/COEP headers.
