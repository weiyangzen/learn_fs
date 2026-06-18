# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-opfs-wl.c-pp.js

## Purpose
This file installs the `opfs-wl` VFS, a variant of the standard wasm OPFS VFS that uses browser Web Locks for SQLite `xLock()`/`xUnlock()` behavior. It shares the common OPFS async proxy machinery with the regular `opfs` VFS, but changes the lock policy so that browser-managed Web Locks can provide stricter FIFO-style lock distribution under contention.

## Important APIs, Types, and Functions
The bootstrap initializer defines `installOpfsWlVfs(options)` and queues it in `sqlite3ApiBootstrap.initializersAsync`. It depends on `sqlite3.opfs.initOptions()`, `sqlite3.opfs.createVfsState()`, the common VFS state's `bindVfs()`, `opRun()`, metrics counters, timing helpers, and `__openFiles`. The VFS name is fixed to `opfs-wl`. The two VFS-specific methods supplied to `bindVfs()` are `xLock(pFile, lockType)` and `xUnlock(pFile, lockType)`.

When OO1 is present, the post-registration callback installs `sqlite3.oo1.OpfsWlDb`, a `DB` subclass that normalizes constructor arguments and forces `opt.vfs` to this VFS name. It also exposes `OpfsWlDb.importDb = opfsUtil.importDb`, reusing the common OPFS import helper.

## Control Flow
On bootstrap, the file returns immediately if `sqlite3.opfs` is unavailable or the config disables `vfs['opfs-wl']`. Async installation normalizes options for `opfs-wl`; a falsy result means the VFS is disabled by URL/config and the top-level sqlite3 object is returned without registration. Otherwise `createVfsState()` builds the shared state and `bindVfs()` registers a VFS whose methods are the common OPFS methods plus the Web-Lock-specific lock/unlock callbacks.

`xLock()` starts metrics timing, retrieves the open file record for `pFile`, calls `opRun('xLock', pFile, lockType)`, and records `f.lockType` only on success. `xUnlock()` mirrors that flow with `opRun('xUnlock', ...)`. Unlike the regular `opfs` wrapper, it does not locally skip redundant lock calls when the file already has a lock; it delegates every lock transition to the async half, where the Web Locks policy lives.

## State and Persistence Behavior
This file itself keeps no persistent storage state. Per-file runtime state is the shared `__openFiles[pFile].lockType`, metrics counters, and the common OPFS VFS state. Actual database persistence, OPFS file access, import behavior, and async proxy communication are delegated to the shared OPFS implementation. Lock ordering depends on browser Web Locks rather than SQLite-visible file contents.

## Dependencies and Integration Points
The file is non-Node-only and is appended after `opfs-common-shared.c-pp.js`. It requires `sqlite3.opfs` helpers, the async OPFS proxy, worker-capable OPFS support, and Web Locks support in the async half. It integrates with sqlite3 initialization through `initializersAsync` and with OO1 through `sqlite3.oo1.OpfsWlDb`. The officially undocumented `opfs-wl-disable` URL/config handling is delegated to `initOptions()`.

## Risks and Edge Cases
Functional behavior is expected to match the regular `opfs` VFS except for contention fairness. Web Locks availability and browser scheduling determine the benefit; the comments explicitly say fairer lock distribution is likely but not guaranteed. Because every lock/unlock crosses the proxy, incorrect shared-state assumptions in the async half would affect database availability. This variant deliberately does not install the busy-timeout post-open callback used by `opfs`, so applications that relied on that default must configure busy timeout themselves.

## Test Signals
Tests should verify installation success/failure under config disable and missing OPFS support, correct registration under `opfs-wl`, OO1 `OpfsWlDb` construction, import helper attachment, basic create/read/write persistence, and multi-worker or multi-tab contention where lock requests are serviced through Web Locks. Regression checks should compare SQL behavior against the standard `opfs` VFS while observing differences in lock fairness and busy-timeout defaults.
