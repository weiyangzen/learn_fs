# sources/storage-engines/sqlite/ext/wasm/api/post-js-header.js

## Purpose

This header opens `Module.runSQLite3PostLoadInit()`, the intentionally verbose post-load entry point called by `extern-post-js.c-pp.js` after Emscripten has loaded the wasm module. It creates the scope into which the full SQLite JavaScript API constellation is concatenated.

## Important APIs and control flow

The file assigns `Module.runSQLite3PostLoadInit = async function(sqlite3InitScriptInfo, EmscriptenModule, sqlite3IsUnderTest) { ... }`. On entry it deletes `EmscriptenModule.runSQLite3PostLoadInit` to avoid exposing the hook after use. The opened function scope is then filled by the prologue, wasm utilities, struct binder, C API glue, OO API, worker API, VFS/vtab helpers, OPFS VFSes, and finally closed by `post-js-footer.js`.

The design explicitly avoids `Module.postRun` because its timing changed across Emscripten versions. The function name is deliberately unlikely to collide with Emscripten symbols.

## State, persistence, dependencies, and risks

This file creates bootstrap-time control state rather than database state. Its correctness depends on concatenation order: the footer must close the function, and all intermediate files must run in this scope after wasm load but before `sqlite3ApiBootstrap()` is called. It also depends on `extern-post-js.c-pp.js` invoking this function on the Emscripten module returned by the original initializer.

Risks are mostly build-order and integration risks: missing footer syntax would break the generated JS, `postRun`-like timing assumptions must not be reintroduced, and future Emscripten symbol collisions are mitigated only by naming. Test signals are parse success of the generated amalgam, one-shot deletion of the hook, correct visibility of `sqlite3InitScriptInfo` and `EmscriptenModule` to the footer, and successful bootstrap of downstream API initializers.
