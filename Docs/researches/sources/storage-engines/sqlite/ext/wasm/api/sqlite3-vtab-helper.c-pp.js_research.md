# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-vtab-helper.c-pp.js

## Purpose
This file installs `sqlite3.vtab`, a JavaScript helper namespace for implementing SQLite virtual tables in wasm. It is active only when the wasm exports include `sqlite3_declare_vtab`, meaning virtual table support exists in the build. Its job is to make pointer-heavy `sqlite3_module`, `sqlite3_vtab`, `sqlite3_vtab_cursor`, and `sqlite3_index_info` interactions safer and more idiomatic from JavaScript.

## Important APIs, Types, and Functions
It augments `capi.sqlite3_index_info.prototype` with `nthConstraint(n, asPtr)`, `nthConstraintUsage(n, asPtr)`, and `nthOrderBy(n, asPtr)`, each performing pointer arithmetic and wrapping the target struct or returning its pointer. It defines `StructPtrMapper(name, StructType)` and uses it to expose `vtab.xVtab` and `vtab.xCursor`, each with `create(ppOut)`, `get(pCObj)`, `unget(pCObj)`, `dispose(pCObj)`, and `StructType`.

Other helpers include `vtab.xIndexInfo(pIdxInfo)`, `vtab.xError(methodName, err, defaultRc)`, `vtab.xRowid(ppRowid64, value)`, `vtab.setupModule(opt)`, and `capi.sqlite3_module.prototype.setupModule(opt)`.

## Control Flow
The initializer exits immediately in builds without virtual table support. For index-info helpers, calls validate bounds against `$nConstraint` or `$nOrderBy`, calculate offsets using struct `sizeof`, and return false when out of range. The pointer mapper closes over a `Map` keyed by C pointer values. `create()` allocates a new struct wrapper, stores its pointer into SQLite's output pointer, and maps the pointer to the wrapper. `get()` retrieves without transferring ownership. `unget()` removes the mapping so the caller must dispose. `dispose()` ungets and disposes in one step.

`setupModule()` builds or receives a `sqlite3_module`, normalizes `xCreate`/`xConnect` and `xDestroy`/`xDisconnect` when one side is `true`, optionally wraps module methods in exception-catching adapters, installs methods, and fills `$iVersion` if it is still zero. With `catchExceptions`, `xCreate` and `xConnect` handlers also allocate an SQLite error string in `pzErr` for non-allocation exceptions.

## State and Persistence Behavior
The helper's main state is in per-mapper JavaScript `Map` instances that associate live C struct pointers with JS wrapper objects. Those maps must be cleaned by calling `unget()`/`dispose()` at the correct SQLite lifecycle points; otherwise wrappers and their wasm allocations can leak. No persistent database or filesystem state is modified by this file.

## Dependencies and Integration Points
The implementation depends on `sqlite3.wasm` pointer helpers, `sqlite3.capi` struct binders, `sqlite3.SQLite3Error`, `sqlite3.WasmAllocError`, and `sqlite3.config.error`. It integrates directly with SQLite virtual table method lifecycles: `xCreate`, `xConnect`, `xBestIndex`, `xOpen`, `xClose`, `xDisconnect`, `xDestroy`, `xRowid`, and update/transaction hooks. `setupModule()` uses `sqlite3_module.installMethods()` from the struct binder layer.

## Risks and Edge Cases
The most important risk is ownership confusion. `get()` returns an object that must not be disposed by the caller, while `unget()` transfers disposal responsibility. Forgetting to unmap cursors or vtabs at failure paths leaks JS/wasm wrapper state. Letting exceptions escape virtual table methods without `catchExceptions` causes undefined behavior across the C ABI. `xError()` only logs if `xError.errorReporter` is a function and maps unknown errors to `SQLITE_ERROR`, which can hide detailed causes unless callers inspect logs. `setupModule()` mutates the passed `methods` object when resolving `true` aliases.

## Test Signals
Tests should cover pointer mapper lifecycle for vtabs and cursors, out-of-range index-info access returning false, pointer-return mode, `xRowid()` writing 64-bit rowids, exception-to-result-code mapping including `WasmAllocError`, `SQLite3Error`, and default cases, `xCreate`/`xConnect` alias preservation, automatic `$iVersion` selection for v1 through v4 method sets, and cleanup on `setupModule()` failure when it created the module object.
