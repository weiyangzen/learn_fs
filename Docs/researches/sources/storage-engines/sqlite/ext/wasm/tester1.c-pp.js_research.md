# sources/storage-engines/sqlite/ext/wasm/tester1.c-pp.js

## Purpose
`tester1.c-pp.js` is the main functional and regression harness for the SQLite WASM JavaScript API. It is preprocessed by `c-pp` so the same source can produce classic script and ES module variants. It can run in the UI thread or a worker, and it validates core C API bindings, WASM utility helpers, `oo1` DB/Stmt wrappers, VFSes, UDFs, virtual tables, storage backends, hooks, sessions, OPFS, SAHPool, SEE-gated paths, and selected bug reports.

## Important APIs, Types, And Functions
The file defines a mini framework in `TestUtil`: `assert`, `mustThrow`, `mustThrowMatching`, `throwIf`, `throwUnless`, `TestGroup`, `addGroup`, `addTest`, `runTests`, and `checkHeapSize`. Predicate helpers include `isUIThread()`, `isWorker()`, `haveWasmCTests()`, and `hasOpfs()`. Shared test helpers include `T.seeBaseCheck()` for SEE encryption checks and `T.opfsCommon` methods for OPFS/OPFS-WL sanity, import/export, and utility APIs. It initializes `sqlite3InitModule`, sets `__isUnderTest`, stores `capi` and `wasm`, and exposes `S` for local debugging.

## Control Flow
Startup configures logging to DOM nodes or `postMessage`, defines all test groups, imports/initializes sqlite3, logs version/VFS/pointer information, then runs groups sequentially. Each group can be skipped by predicate; each test receives the sqlite3 namespace and a per-group state object. Failures abort the queue, mark the UI or worker result as failed, and force a heap-size report. The groups cover basic config/error constants, WASM allocators and typed memory helpers, struct binding, pstack, randomness, DB/Stmt lifecycle, `exec`/select helpers, authorizer, metadata, db export/import, scalar/aggregate/window UDFs, ATTACH and read-only behavior, C-side test exports, JS virtual-table modules, collations, kvvfs, hooks, auto-extension, session changesets, OPFS/OPFS-WL, OPFS SAHPool, miscellaneous statement APIs, interrupt/error-message APIs, and specific regression reports.

## State And Persistence Behavior
Most tests use transient DBs, but some touch persistent browser stores: kvvfs in session/local/transient storage, OPFS files, OPFS-WL files, SAHPool file pools, and optional SEE-encrypted files. The harness carefully closes DBs/statements in `finally`, uses `db.onclose` cleanup callbacks for installed functions/structs/modules, restores pstack/scoped allocations, removes temporary VFSes, and unlinks OPFS/kvvfs files where appropriate. `localStorage` stores the UI log-order checkbox state.

## Dependencies And Integration Points
It depends on the generated sqlite3 JS/WASM loader, browser DOM or Worker APIs, c-pp substitution (`@sqlite3.js@`, `target:es6-module`, query expansion), optional BigInt/MEMORY64 support, optional compile flags (`SQLITE_WASM_ENABLE_C_TESTS`, FTS5, vtab, session, window, hooks, OPFS, SAHPool, SEE), and many SQLite JS API namespaces: `capi`, `wasm`, `oo1`, `vtab`, `kvvfs`, `opfs`, and `installOpfsSAHPoolVfs`.

## Risks And Test Signals
This file is intentionally broad, so risks include environment-sensitive skips hiding regressions, reliance on private test-only APIs, long synchronous tests in browsers, persistent browser state contaminating results, incomplete cleanup after early failure, and c-pp query/conditional output drift. Strong signals are a final PASS in both UI and worker modes, expected skip messages for unavailable optional features, stable assertion counts for a given build, no leaked statements or open DBs, no unexpected heap growth reports, successful OPFS/SAHPool cleanup, and regression tests passing for referenced forum/issues.
