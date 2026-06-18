# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs.c-pp.js

## Purpose
This file installs the standard `opfs` sqlite3 VFS for wasm builds. It is the synchronous JavaScript half of an OPFS-backed VFS that proxies asynchronous browser file operations through a second worker (`sqlite3-opfs-async-proxy.js`) so SQLite can call a synchronous `sqlite3_vfs` interface. It is intended to run only where dedicated workers, `SharedArrayBuffer`, Atomics, and OPFS support are available.

## Important APIs, Types, and Functions
The initializer defines `installOpfsVfs(options)` and appends an async bootstrap task that calls it. Publicly visible behavior is registration of an SQLite VFS named `opfs`, and, when OO1 is enabled, `sqlite3.oo1.OpfsDb`. The function uses `sqlite3.opfs.initOptions('opfs', options)`, `sqlite3.opfs.createVfsState()`, and the returned state's `vfs.bindVfs()`, `opRun()`, timing helpers, metrics counters, and `__openFiles`.

The only VFS-specific methods in this file are `xLock()` and `xUnlock()`. All storage, path handling, file I/O, proxying, metrics setup, and import mechanics are provided by common OPFS code loaded before this wrapper.

## Control Flow
At startup, the initializer exits when `sqlite3.opfs` is missing or `sqlite3.config.disable.vfs.opfs` is set. `installOpfsVfs()` normalizes options and exits as a no-op when OPFS is disabled by options or URL. For active installs, `createVfsState()` prepares the VFS struct and shared proxy state. `bindVfs()` receives the lock/unlock overrides and a post-registration callback, then handles registration and common method installation.

`xLock()` records timing and metrics, looks up the open file object, and only calls `opRun('xLock', pFile, lockType)` if the file was previously unlocked. SQLite lock types are tracked in `f.lockType`, but the OPFS implementation treats actual file locks as exclusive. Re-locking an already locked file only updates the tracked lock type. `xUnlock()` calls the proxy only when transitioning to `SQLITE_LOCK_NONE` from a locked state, then records the new lock type on success.

After registration, the OO1 integration creates `OpfsDb`, a DB subclass forcing this VFS. It assigns `OpfsDb.importDb` to the shared `opfsUtil.importDb`. It also sets a VFS post-open callback that applies `sqlite3_busy_timeout(db, 10000)` for this VFS, retained for compatibility even though comments call it inconsistent with core open APIs.

## State and Persistence Behavior
This wrapper owns no persistent state directly. Runtime state includes lock type on entries in `__openFiles`, metrics counts/timings, and whatever proxy state the common OPFS layer holds. Persistence is in OPFS through the async proxy and common implementation. Lock state is deliberately simplified: SQLite's fine-grained lock levels are represented to SQLite, while OPFS-level access is exclusive.

## Dependencies and Integration Points
The file is non-Node-only and depends on `sqlite3.opfs` being initialized by shared OPFS modules. It requires a dedicated worker environment and SharedArrayBuffer/Atomics because synchronous C calls must block while the async proxy performs browser file operations. It integrates with `sqlite3ApiBootstrap.initializersAsync`, `sqlite3.config.warn`, OO1 DB construction, and `sqlite3.capi.sqlite3_busy_timeout`.

## Risks and Edge Cases
The install Promise can reject if the async proxy cannot load, OPFS is unavailable, the code runs on the wrong thread, or SharedArrayBuffer is unavailable due to missing COOP/COEP headers. Lock handling deliberately avoids redundant proxy calls, so correctness depends on `__openFiles[pFile].lockType` staying in sync with the async half. The retained default busy timeout may surprise callers expecting sqlite3 core defaults. The install callback catches rejection and warns, so applications must inspect VFS availability if OPFS is required.

## Test Signals
Relevant tests include disabled/no-op installs, successful `opfs` VFS registration in a worker, graceful warning on missing SAB/OPFS/proxy support, basic open/write/read persistence, lock/unlock transitions under concurrent access, `OpfsDb` constructor behavior, `OpfsDb.importDb`, and the post-open busy-timeout setting. Tests should also cover contention and redundant lock transitions to ensure no unnecessary proxy unlock or lock calls corrupt state.
