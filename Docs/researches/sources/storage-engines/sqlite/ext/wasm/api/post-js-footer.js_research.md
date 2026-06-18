# sources/storage-engines/sqlite/ext/wasm/api/post-js-footer.js

## Purpose

This footer closes the `Module.runSQLite3PostLoadInit()` function opened by `post-js-header.js`. It assembles bootstrap configuration after the wasm module is loaded, calls `globalThis.sqlite3ApiBootstrap()`, deletes the bootstrap helper, and returns the promise that becomes the public `sqlite3InitModule()` result.

## Important APIs and control flow

The footer runs inside `Module.runSQLite3PostLoadInit(sqlite3InitScriptInfo, EmscriptenModule, sqlite3IsUnderTest)`, so those arguments and Emscripten-generated locals are in scope. It builds `bootstrapConfig` by combining the detected wasm memory and exports, `globalThis.sqlite3ApiBootstrap.defaultConfig`, and optional `globalThis.sqlite3ApiConfig`. Export detection handles newer Emscripten globals (`wasmExports`), module properties (`EmscriptenModule.wasmExports`), and older `EmscriptenModule.asm`.

After debug logging, it calls `globalThis.sqlite3ApiBootstrap(bootstrapConfig)`, deletes `globalThis.sqlite3ApiBootstrap`, and returns the resulting promise. Any exception is logged as a bootstrap error and rethrown.

## State, persistence, dependencies, and risks

The file mutates only bootstrap-time global state. No database persistence occurs here. It depends on the header-created function scope, Emscripten's wasm memory/export shape, `sqlite3ApiBootstrap.defaultConfig`, optional client config, and the initializer chain populated by earlier post-JS fragments.

Risks include Emscripten export-shape drift, clients supplying incompatible `sqlite3ApiConfig`, bootstrap deletion preventing later re-bootstrap attempts in the same JS realm, and errors in any initializer surfacing only after wasm load. Test signals include successful bootstrap under supported Emscripten versions, custom config merging, debug output when enabled, cleanup of `globalThis.sqlite3ApiBootstrap`, and rejection propagation when an initializer throws.
