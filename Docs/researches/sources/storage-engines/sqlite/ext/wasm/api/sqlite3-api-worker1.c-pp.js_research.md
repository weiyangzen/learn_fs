# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-worker1.c-pp.js

## Purpose
This file installs `sqlite3.initWorker1API()`, the initializer for SQLite WASM "Worker API #1". It exposes a small message-driven database API for Worker threads, implemented on top of `sqlite3.oo1.DB`, so main-window code can open databases, execute SQL, export database bytes, close handles, and inspect serializable configuration without directly sharing SQLite objects across thread boundaries.

## Important APIs, Types, and Functions
The public entry point is `sqlite3.initWorker1API()`. It must run in a Worker, must be called once per Worker, installs `globalThis.onmessage`, and posts `{type:'sqlite3-api', result:'worker1-ready'}` when initialized.

The message API supports `open`, `close`, `exec`, `export`, `config-get`, and a testing-only `toss`. Message envelopes may include `type`, `messageId`, `dbId`, and operation-specific `args`. Responses copy `messageId`, include a `dbId` when available, and place operation output under `result`. Errors are normalized to `{type:'error', result:{operation,message,errorClass,input,stack?}}`.

Internal state lives in `wState`: `dbList` tracks opened `DB` instances in least-recently-opened/default order, `idSeq` and `idMap` generate stable opaque database IDs per DB object, `xfer` accumulates transferable buffers for `postMessage`, and `dbs` maps IDs to live DB objects. `getDbId()`, `affirmDbOpen()`, `getMsgDb()`, and `getDefaultDbId()` implement ID lookup and default selection.

## Control Flow
When initialized, the code validates that it is running in a Worker, captures `sqlite3.oo1.DB`, defines state helpers, and assigns an async `onmessage` dispatcher. Each inbound `ev.data` is routed by `type` to a `wMsgHandler` method. The method returns a plain object or throws; the dispatcher wraps thrown errors, fills in the default DB ID if the request did not provide one, attaches timing fields (`workerReceivedTime`, `workerRespondTime`, `departureTime`), and posts the response with any accumulated transfer list.

`open` normalizes `args.filename` to `""` when absent, forwards `filename` and `vfs` to the DB constructor, stores the DB, returns the actual filename, new `dbId`, `db.dbVfsName()`, and a `persistent` boolean based on whether the DB uses the `opfs` VFS. `close` is idempotent for unknown/missing DB IDs and optionally unlinks the file through `sqlite3__wasm_vfs_unlink()` after closing. `exec` converts string args to `{sql}`, rejects `rowMode:'stmt'`, installs a callback proxy when `args.callback` is a string message type, optionally computes change counts and last insert rowid, and sends a sentinel callback row with `rowNumber:null` and `row:undefined`. `export` calls `sqlite3_js_db_export()` and transfers the resulting `Uint8Array` buffer. `config-get` returns `bigIntEnabled`, `sqlite3.version`, and `sqlite3_js_vfs_list()`.

## State and Persistence Behavior
Database lifetime is Worker-local. Multiple DBs may be open simultaneously, but all operations execute serially on the Worker event loop, and calls without `dbId` use the first open DB. IDs intentionally include random components because pointer values can be reused and separate Worker instances previously collided on generated IDs.

Persistence depends on the selected VFS and filename. This file does not implement storage itself; it delegates to `oo1.DB`, `sqlite3_js_db_uses_vfs()`, `sqlite3_js_db_export()`, and VFS unlink helpers. `close({unlink:true})` deletes the backing file only if there was a known filename and VFS pointer. `export` returns a snapshot byte array and marks its buffer as transferable to avoid copying.

## Dependencies and Integration Points
The file is compiled only when OO API #1 is not omitted. It requires `sqlite3.util`, `sqlite3.oo1.DB`, `sqlite3.capi.sqlite3_js_db_uses_vfs`, `sqlite3.capi.sqlite3_js_vfs_list`, `sqlite3.capi.sqlite3_js_db_export`, `sqlite3.capi.sqlite3_last_insert_rowid`, and internal WASM utility functions `sqlite3__wasm_db_vfs` and `sqlite3__wasm_vfs_unlink`.

Its primary client-facing integration is `sqlite3-worker1-promiser.js`, which wraps the message protocol in Promises and reduces ordering hazards. Row streaming integrates with `postMessage()` by treating a string `callback` option as a message type for row events. Blob transfer optimization is coordinated through `db._blobXfer`, which the OO API can populate during result creation.

## Risks and Edge Cases
The API is intentionally minimal and not safe for recursive use from row callbacks; a nested `exec` waits behind the current `exec` because the Worker thread is occupied. Message ordering can also be surprising: many messages can queue before an `open` failure is known, causing later operations to fail.

Defaulting to the first opened DB is convenient but can mask missing or stale `dbId`s in multi-DB clients. `close` treats an unknown DB as a no-op, so a client may believe it closed or unlinked a database when no live DB matched. `exec` mutates the input options object for results and callback restoration; structured-cloned inputs avoid sharing with the sender, but tests should still treat the response object as modified options, not a separate result envelope.

`persistent` currently checks only the `opfs` VFS, so other persistent VFSes may not be reflected. `lastInsertRowId` returns whatever `sqlite3_last_insert_rowid()` reports after all SQL statements, even if no INSERT occurred. BigInt-related change counts or row IDs can throw in builds without BigInt support.

## Test Signals
Test from an actual Worker and verify the ready message, rejection when called on the main thread, `open` with memory and named VFS databases, default DB routing, unknown `dbId` errors for operations requiring a DB, idempotent close, unlink behavior, row callback streaming including the final sentinel, `countChanges` 32-bit and 64-bit modes, `lastInsertRowId`, export transferability, `config-get` VFS listing, error envelope stack capture, and queued-message behavior when `open` fails with `simulateError`.
