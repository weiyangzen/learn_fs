# sources/storage-engines/sqlite/src/loadext.c

## Purpose

`loadext.c` implements SQLite's loadable-extension support. It builds the `sqlite3_api_routines` thunk passed to extensions, implements dynamic shared-library loading for `sqlite3_load_extension()`, tracks per-connection dynamic-library handles for cleanup, exposes `sqlite3_enable_load_extension()`, and manages the process-global auto-extension list used to initialize statically linked extensions on every new connection.

When `SQLITE_OMIT_LOAD_EXTENSION` is defined, dynamic loading code is omitted, but auto-extension registration/loading still exists and passes a NULL API thunk to auto extensions.

## Important APIs, Types, and Functions

- `sqlite3Apis` is the ordered `sqlite3_api_routines` table exported to extensions. Omitted SQLite features map corresponding entries to NULL, and newer APIs are appended to preserve ABI compatibility.
- `sqlite3LoadExtension()` is the internal dynamic loader. It opens the shared library, locates the entry point, calls it, and records the library handle.
- `sqlite3_load_extension()` is the public mutex/API-exit wrapper around `sqlite3LoadExtension()`.
- `sqlite3CloseExtensions()` closes all dynamic libraries associated with a database connection.
- `sqlite3_enable_load_extension()` toggles `SQLITE_LoadExtension` and `SQLITE_LoadExtFunc` flags on the connection.
- `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, `sqlite3_reset_auto_extension()`, and `sqlite3AutoLoadExtensions()` manage the global auto-extension list.
- `sqlite3AutoExtList` stores `nExt` and a realloc-grown array of extension init function pointers. `wsdAutoext` abstracts writable-static-data versus `SQLITE_OMIT_WSD` builds.

## Control Flow

At the top of the file, `SQLITE_CORE` is forced before including `sqlite3ext.h` so the core sees real API symbols instead of extension macro remaps. Conditional defines replace unavailable API functions with NULL table entries when features such as UTF-16, authorizers, virtual tables, WAL, deserialize, carray, or deprecated APIs are omitted.

Dynamic loading starts in `sqlite3_load_extension()`, which enters the connection mutex, calls `sqlite3LoadExtension()`, normalizes the result through `sqlite3ApiExit()`, and leaves the mutex. The internal loader first checks `SQLITE_LoadExtension`; loading is disabled by default for security. It rejects oversized paths and empty filenames, tries to open the file as provided, and on Unix/Windows also retries with platform suffixes (`.so`, `.dylib`, or `.dll`).

After opening a library through the VFS dynamic-loading methods, it resolves the requested entry point or the default `sqlite3_extension_init`. If the default is missing and no entry point was specified, it derives `sqlite3_X_init` from the filename by taking the basename, skipping a leading `lib`, lowercasing ASCII alphabetics up to the first dot, and retrying with digits included on the second pass.

The entry point is called as `xInit(db, &zErrmsg, &sqlite3Apis)`. `SQLITE_OK_LOAD_PERMANENTLY` is treated as success without recording the handle for close. Any other non-zero code becomes `SQLITE_ERROR` with an initialization message and the library handle is closed. On success, the handle is appended to `db->aExtension`, reallocating and copying the existing handle array, so `sqlite3CloseExtensions()` can close each handle when the connection closes.

`sqlite3_enable_load_extension()` is a simple mutex-protected flag toggle. Enabling sets both dynamic loading and the SQL `load_extension()` function flag; disabling clears both. API armor validates the DB handle when enabled.

Auto-extension registration calls `sqlite3_initialize()` unless autoinit is omitted, locks `SQLITE_MUTEX_STATIC_MAIN`, avoids duplicate function pointers, reallocates the global array, and appends the init pointer. Cancellation swaps the last entry into the removed slot. Reset frees the global array. `sqlite3AutoLoadExtensions()` early-outs if no entries exist, then repeatedly locks just long enough to read the next pointer, unlocks, and invokes the extension initializer against the connection. This allows callbacks to modify the auto-extension list without holding the global mutex across user code.

## State and Persistence Behavior

Per-connection dynamic extension state is stored in `db->aExtension` and `db->nExtension`. It persists until connection close, where `sqlite3CloseExtensions()` must run while holding `db->mutex` and calls `sqlite3OsDlClose()` for each handle.

Process-global auto-extension state lives in `sqlite3Autoext` or the writable-static-data substitute. It persists across connections until explicitly reset and is protected by the static main mutex. The array stores function pointers only; it does not own extension-specific resources beyond the pointer list allocation.

The API routine table is static const state. It encodes build capabilities at compile time; extensions must check SQLite version and NULL entries before using optional APIs.

## Dependencies and Integration Points

This file includes `sqlite3ext.h` and `sqliteInt.h`. It integrates with the VFS dynamic loader (`sqlite3OsDlOpen`, `sqlite3OsDlSym`, `sqlite3OsDlError`, `sqlite3OsDlClose`), connection flags, mutexes, SQLite allocators, initialization, and error reporting.

The SQL `load_extension()` function is guarded elsewhere by `SQLITE_LoadExtFunc` (notably in `func.c`), while this file's C API gate uses `SQLITE_LoadExtension`. Connection close calls `sqlite3CloseExtensions()` from `main.c`, and opening a DB invokes `sqlite3AutoLoadExtensions()` from `main.c`. Test-facing wrappers for loading and enabling extensions appear in `src/test1.c`; `src/test_loadext.c` is a specific test extension.

The ordered `sqlite3Apis` table is ABI-sensitive. New API entries are appended by version blocks, including current entries through `sqlite3_str_free`, optional carray bindings, and `sqlite3_incomplete`. Changing order would break loadable extensions compiled against `sqlite3ext.h`.

## Risks and Edge Cases

Dynamic loading is security-sensitive. Loading is intentionally disabled by default, empty filenames are rejected to avoid linking the running application, and path length is bounded to avoid platform `dlopen()` issues. Any change to flag gating can expose the SQL `load_extension()` function or the C loader unexpectedly.

Entry-point derivation is compatibility-sensitive and platform-sensitive. Filename parsing must handle `/` and `\` on Windows, a leading `lib`, case folding, dots, and digits on the second attempt. Error reporting must include both SQLite's message and VFS dynamic-loader error without leaking allocated buffers.

Resource ownership is subtle after `xInit()`. `SQLITE_OK_LOAD_PERMANENTLY` intentionally leaves the handle open without adding it to the close list. Normal success must add the handle to `db->aExtension`; failure must close it. If appending the handle array fails after successful initialization, the current code returns NOMEM without closing the just-loaded handle, which is consistent with an extension that may have registered state but is a resource-retention risk to keep in mind.

Auto-extension callbacks run outside the global mutex, so the loop must tolerate registration/cancellation/reset during loading. It reads the list one entry at a time under lock and stops on errors by setting the connection error message. Duplicate registration is ignored. API armor affects NULL pointer behavior for registration/cancellation.

The API thunk contains many NULLs under feature-omit macros; extensions that fail to check optional pointers can crash. Table order and conditional entries are therefore high-risk for refactors.

## Test Signals

Relevant tests include `src/test_loadext.c`, TCL wrappers in `src/test1.c` for `sqlite3_load_extension` and `sqlite3_enable_load_extension`, shell `.load` behavior in `src/shell.c.in`, and extension/auto-extension usage such as `test_multiplex.c` and shell auto-extension reset checks. Build variants omitting UTF-16, virtual tables, WAL, deprecated APIs, load extension, and writable static data are important because they change API table entries and code paths.

Focused regression tests should cover disabled-by-default loading, enabling/disabling both C and SQL loaders, missing files and suffix retries, explicit and derived entry points, no-entry error messages, extension init failures and `zErrmsg`, `SQLITE_OK_LOAD_PERMANENTLY`, close-time handle cleanup, duplicate auto-extension registration, cancellation, reset, auto-extension init failure, and concurrent auto-extension list changes.
