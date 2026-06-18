# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-api-prologue.js

## Purpose
This file defines the one-time `globalThis.sqlite3ApiBootstrap()` entry point used by the generated SQLite WebAssembly JavaScript bundle. It builds the top-level `sqlite3` namespace, validates the WASM/environment configuration, seeds the C-style API namespace (`sqlite3.capi`), the WASM helper namespace (`sqlite3.wasm`), internal `sqlite3.util`, error classes, allocator wrappers, pseudo-stack helpers, and several JS convenience wrappers around C APIs. It also owns the initializer queues that later amalgamated fragments use to install OO APIs, VFSes, OPFS support, kvvfs, virtual table helpers, and worker APIs.

## Important APIs, Types, and Functions
`sqlite3ApiBootstrap(apiConfig)` is asynchronous and returns the initialized `sqlite3` namespace after synchronous initializers and `asyncPostInit()` complete. The config accepts delayed-function properties for `exports`, `memory`, `functionTable`, and `wasmfsOpfsDir`, supports allocator export names, logging functions, `bigIntEnabled`, and `disable.vfs` flags.

`SQLite3Error` and `WasmAllocError` are public exception types. `SQLite3Error.toss()` and `WasmAllocError.toss()` are expression-friendly throw helpers, and both attach SQLite-style result codes (`SQLITE_ERROR` and `SQLITE_NOMEM` respectively).

The file declares placeholders for wrapper APIs installed later by glue code: `sqlite3_bind_blob`, `sqlite3_bind_text`, `sqlite3_create_function_v2`, `sqlite3_create_function`, `sqlite3_create_window_function`, `sqlite3_prepare_v3`, `sqlite3_prepare_v2`, and `sqlite3_exec`. Its comments define the intended JS/WASM conversion semantics for those wrappers.

Directly implemented C-style helpers include `sqlite3_randomness()`, `sqlite3_wasmfs_opfs_dir()`, `sqlite3_wasmfs_filename_is_persistent()`, `sqlite3_js_db_uses_vfs()`, `sqlite3_js_vfs_list()`, `sqlite3_js_db_export()`, `sqlite3_js_db_vfs()`, `sqlite3_js_aggregate_context()`, `sqlite3_js_posix_create_file()`, deprecated `sqlite3_js_vfs_create_file()`, `sqlite3_js_sql_to_string()`, `sqlite3_db_config()`, `sqlite3_value_to_js()`, `sqlite3_values_to_js()`, `sqlite3_result_error_js()`, `sqlite3_result_js()`, `sqlite3_column_js()`, `sqlite3_preupdate_new_js()`, `sqlite3_preupdate_old_js()`, `sqlite3changeset_new_js()`, `sqlite3changeset_old_js()`, and `sqlite3_js_retry_busy()`.

The `wasm` namespace starts with `exports`, `memory`, `pointerSize`, `bigIntEnabled`, `functionTable`, `alloc`, `realloc`, `dealloc`, `allocFromTypedArray()`, `compileOptionUsed()`, and `pstack`. `pstack` exposes `restore`, `alloc`, `allocChunks`, `allocPtr`, `call`, and read-only `pointer`, `quota`, and `remaining` properties.

## Control Flow
The bootstrap function first short-circuits repeated calls by returning the previously initialized object and warning that later config and external initializers are ignored. On the first call it merges defaults with caller/global config, resolves delayed config properties, validates OPFS mount syntax, constructs `capi`, `wasm`, `util`, and error classes, then installs allocator wrappers around the configured exported malloc/free/realloc symbols.

It then installs early convenience functions that rely on WASM exports and helpers supplied by later glue. Synchronous fragments register callbacks in `sqlite3ApiBootstrap.initializers`; the bootstrap iterates that list in append order and passes each the partially built `sqlite3` object. After that, `asyncPostInit()` processes `initializersAsync`, deletes internal-only helpers outside test mode, stores script/instantiate metadata only in test mode, removes global/default config objects, deletes the bootstrap symbol, and resolves to the public `sqlite3` namespace with `asyncPostInit`, `scriptInfo`, and `emscripten` removed.

## State and Persistence Behavior
Persistent bootstrap state is intentionally narrow: `sqlite3ApiBootstrap.sqlite3` caches the first result, and the global bootstrap/config symbols are deleted after use to prevent configuration drift. `wasm.compileOptionUsed()` caches the all-options map for no-argument calls. `sqlite3_wasmfs_opfs_dir()` lazily detects and initializes WASMFS OPFS support once, then caches either the mount point or an empty string. `wasm.pstack` is transient stack-like WASM heap storage; callers must save and restore the pointer.

Database persistence is not implemented here directly, but this file exposes persistence-aware helpers. `sqlite3_js_db_export()` serializes a database into a `Uint8Array` using WASM heap pointers and frees SQLite-owned output with `sqlite3_free`. `sqlite3_wasmfs_filename_is_persistent()` reports whether a path falls under the configured WASMFS OPFS mount. `sqlite3_js_posix_create_file()` and deprecated `sqlite3_js_vfs_create_file()` import byte data into the active filesystem/VFS, allocating temporary WASM buffers for JS byte arrays.

## Dependencies and Integration Points
This file requires a WASM exports object with SQLite allocator exports, pstack exports, `sqlite3_libversion`, `sqlite3_randomness`, and later glue-provided symbols. It depends on `sqlite3-api-glue.c-pp.js`/`whwasmutil.js` style code to populate pointer utilities, heap views, `xWrap`, scoped allocation, string conversion, function table helpers, struct binders, and the many C API wrappers declared as placeholders.

The global initializer arrays are the central integration point for the rest of the amalgamation. VFS helpers, kvvfs, OO API, worker APIs, OPFS modules, and testing hooks all plug into this bootstrap through those queues. Script loading metadata from `post-js-header.js` may be attached as `sqlite3.scriptInfo` for async OPFS worker resolution before being removed from the final public object.

## Risks and Edge Cases
The bootstrap is single-use: later calls silently reuse the first environment except for a warning, so mismatched WASM/JS bundles or late config changes are not recoverable without reloading the JS realm. BigInt support controls int64 behavior; APIs such as `sqlite3_js_db_export()` throw without BigInt support.

Memory ownership is a major risk surface. Helpers allocate WASM memory for typed arrays, strings, output pointers, and SQL result values, and rely on correct destructor constants such as `SQLITE_WASM_DEALLOC` or explicit `wasm.dealloc()`/`sqlite3_free()`. Incorrect allocator selection via `useStdAlloc` or custom export names can break APIs such as serialize/deserialize.

`sqlite3_js_vfs_create_file()` is explicitly deprecated because its VFS usage can trigger debug-build assertions or C-level crashes. `sqlite3_js_sql_to_string()` appears to contain a source-level bug: it calls `flexibleString(v)` and compares `x===v`, but `v` is not defined in that scope; callers taking the non-string path would hit a `ReferenceError`. `sqlite3_result_js()` contains a typo in an error message ("Don't not") but the behavior is still to report an SQL error.

## Test Signals
Useful tests include bootstrapping with exported versus imported memory, missing allocator exports, invalid `wasmfsOpfsDir`, repeated bootstrap calls, BigInt disabled builds, `sqlite3_randomness()` with zero-length and large typed arrays, pstack save/restore under exceptions, `sqlite3_js_db_export()` for empty and non-empty schemas, `sqlite3_value_to_js()`/`sqlite3_result_js()` round trips for null/bool/int64/double/text/blob, `sqlite3_db_config()` variants, and exercising `sqlite3_js_sql_to_string()` with typed array and pointer inputs to catch the undefined-variable path.
