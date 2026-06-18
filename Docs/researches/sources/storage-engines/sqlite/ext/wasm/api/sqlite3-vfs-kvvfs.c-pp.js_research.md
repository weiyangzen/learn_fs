# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vfs-kvvfs.c-pp.js

## Purpose
This file installs the JavaScript side of SQLite's `kvvfs` key/value VFS. The native `os_kv.c` and `sqlite3-wasm.c` pieces provide the SQLite VFS and encoding primitives; this file replaces selected record, VFS, and I/O methods so database pages and metadata can be stored in JavaScript `Storage`-like objects such as `localStorage`, `sessionStorage`, or transient in-memory stores. Version 2 adds named transient storage objects, import/export, listeners, and Worker-thread availability for the `sqlite3.kvvfs` interface.

## Important APIs, Types, and Functions
The initializer exits if `sqlite3.config.disable?.vfs?.kvvfs` is set or if `sqlite3_vfs_find("kvvfs")` fails. It consumes and deletes JS plumbing structs `capi.sqlite3_kvvfs_methods` and `capi.KVVfsFile`, then wraps the native singleton returned by `sqlite3__wasm_kvvfs_methods()`.

`KVVfsStorage` implements the Storage interface over a prototype-less object with `key()`, `getItem()`, `setItem()`, `removeItem()`, `clear()`, and `length`. `cache` holds regexes, common C strings (`jrnl`, `sz`), key size, reusable WASM page encode/decode buffers, `storagePool`, builtin storage names, and last-error state. `newStorageObj()`, `installStorageAndJournal()`, `deleteStorage()`, `validateStorageName()`, `storageForZClass()`, `zKeyForStorage()`, and `jsKeyForStorage()` manage storage records and kvvfs key naming.

The low-level override groups are `methodOverrides.recordHandler` (`xRcrdRead`, `xRcrdWrite`, `xRcrdDelete`), `methodOverrides.vfs` (`xOpen`, `xDelete`, `xAccess`, `xRandomness`, `xGetLastError`), `methodOverrides.ioDb` (`xClose`, `xFileControl`, `xSync`, plus disabled debug read/write wrappers), and `methodOverrides.ioJrnl` (mostly copies DB methods). Original native callbacks are retained in `originalMethods` and called where JS only augments behavior.

Public v2 APIs are attached under `sqlite3.kvvfs`: `reserve`, `import`, `export`, `unlink`, `listen`, `unlisten`, `exists`, `estimateSize`, and `clear`. Main-thread Storage builds also expose v1-compatible `capi.sqlite3_js_kvvfs_size()` and `capi.sqlite3_js_kvvfs_clear()`. When OO API #1 is present, `sqlite3.oo1.JsStorageDb` is installed as a DB subclass/wrapper that forces `vfs:'kvvfs'` and validates storage names.

In test builds with vtab support, `sqlite3.kvvfs.create_module()` registers an eponymous inspection virtual table exposing storage name, refcount, open count, transient flag, and db size.

## Control Flow
During bootstrap the file builds the cache, installs builtin storage objects (`.` always, plus `local`/`session` if available), adds `-journal` aliases to the same storage objects, and installs JS function pointers over native struct fields with `wasm.installFunction()`. It disposes the temporary struct wrappers after patching the underlying native structs.

At runtime, `xOpen` validates or synthesizes a storage name, rejects database names ending in `-journal`, creates storage on `SQLITE_OPEN_CREATE`, maps the database and journal name to one shared storage object, increments refcounts for existing storage, wraps the sqlite3_file pointer in `KVVfsFile`, records it in `pFileHandles`, sets output flags, and notifies listeners. `xClose` removes the file handle, decrements refcount, optionally deletes transient storage at refcount zero, calls the original native close, disposes the wrapper, and emits close events.

Record reads and writes are the actual key/value bridge. `xRcrdRead` finds a Storage object by zClass, maps zKey into the correct JS key, reads an ASCII kvvfs-encoded string, copies it through a reusable WASM buffer into the caller buffer, and returns size/status conventions expected by `os_kv.c`. `xRcrdWrite` converts the C string to JS text, stores it, and notifies listeners. `xRcrdDelete` removes the key and notifies listeners. `xGetLastError` pops cached JS exceptions into SQLite's error buffer.

The high-level export path walks matching Storage keys, extracts `sz`, optional `jrnl`, and page records, optionally decodes page strings to `Uint8Array`s using `sqlite3__wasm_kvvfs_decode`, sorts numeric page keys, and returns a JSON-friendly object. Import validates the export object, creates or clears a storage object, writes size/journal/page records, encoding raw `Uint8Array` pages through `sqlite3__wasm_kvvfs_encode`, and installs new storage aliases on success.

## State and Persistence Behavior
`local` and `session` storage names map to browser `localStorage` and `sessionStorage` when available and use keys prefixed as `kvvfs-local-` or `kvvfs-session-` for v1 compatibility and coexistence with unrelated client keys. Other storage names use transient `KVVfsStorage` instances with shorter keys (`sz`, `jrnl`, page numbers). The special `.` storage is a per-thread transient store and is the default fallback for `JsStorageDb` when `sessionStorage` is absent.

Storage objects are reference counted and keep a `files` list so DB and journal handles share the same backing store and so transient stores are not deleted while open. `reserve()` increments or creates storage to keep it alive, `unlink()` decrements/removes non-builtin transient storage when safe, and `deleteAtRefc0` supports delete-on-close semantics. `clear()` wipes matching keys and refuses to clear in-use non-local/session storage.

Listeners are stored per storage object and receive asynchronous `open`, `close`, `write`, `delete`, and `sync` events. Write listeners may request decoded page bytes. Listener exceptions are caught and warned, not propagated into SQLite calls.

## Dependencies and Integration Points
This file depends on native kvvfs structs/functions exposed through `sqlite3-wasm.c`: `sqlite3__wasm_kvvfs_methods()`, `sqlite3__wasm_kvvfs_decode`, `sqlite3__wasm_kvvfs_encode`, and `sqlite3__wasm_kvvfsMakeKey`. It depends on StructBinder wrappers for `sqlite3_vfs`, `sqlite3_io_methods`, `sqlite3_kvvfs_methods`, and `KVVfsFile`, plus WASM helpers for C strings, heap access, function installation, scoped allocation, pointer reads/writes, and pstack.

It integrates with browser `Storage`, the OO `DB` constructor via `JsStorageDb`, the SQLite VFS registry via the preexisting `kvvfs` VFS, `sqlite3_file_control()`/PRAGMA handling, optional virtual table helpers for tests, and the bootstrap `disable.vfs.kvvfs` configuration.

## Risks and Edge Cases
The file documents that kvvfs is for small databases that fit within Web Storage limits, roughly a few megabytes, and is malloc/conversion heavy. Browser storage quotas, synchronous localStorage/sessionStorage behavior, and per-entry overhead can cause failures outside SQLite's direct control.

Storage name validation is strict because native key buffers are fixed-size. Names cannot be empty, too long, contain control characters, or end in `-wal`/`-shm`; `-journal` is only accepted internally during open. `xAccess` intentionally uses behavior that appears inverted relative to the native implementation because it matches observed SQLite expectations; this deserves regression coverage.

The code works around a known corruption issue by intercepting `PRAGMA page_size` changes and effectively disabling page-size mutation before VACUUM. That avoids corruption but can surprise callers expecting page-size changes to take effect. `xRandomness` uses `Math.random()`, not cryptographic randomness. Reusable WASM buffers are intentionally leaked for VFS lifetime because SQLite VFS lacks a JS finalizer hook.

Import has an apparent bug-risk path: its `catch` clears existing storage on failure but does not rethrow the caught exception, so callers may receive success despite a failed import after cleanup. Event listener page decoding uses shared temporary buffers and async callback scheduling; listener code must not assume a stable object beyond copied data. Clearing local/session storage while a DB is open remains allowed for backwards compatibility even though it can disrupt active use.

## Test Signals
Tests should cover bootstrap with kvvfs disabled and unavailable, builtin storage discovery in main thread versus Worker, storage name validation boundaries, opening/closing DB and journal pairs, refcount and delete-on-close behavior, `reserve()`/`unlink()` lifecycle, v1 key compatibility for local/session, transient key format, record read/write/delete error codes, `xAccess` existence semantics, page-size PRAGMA interception, clear refusal for in-use transient storage, import/export with encoded and decoded pages, malformed import cleanup and exception behavior, listener events with and without journal/page decoding, `JsStorageDb` filename normalization, and the test-only virtual table when `sqlite3.__isUnderTest` and vtab support are present.
