# sources/storage-engines/sqlite/ext/wasm/api/pre-js.c-pp.js

## Purpose

This pre-JS fragment runs inside Emscripten's generated `sqlite3InitModule()` after `Module` exists but before Emscripten's main wasm-loading work. It customizes file location and, for supported builds, wasm instantiation so SQLite can reliably find the sidecar `.wasm` file across script-tag, worker, URL-parameter, and ESM scenarios.

## Important APIs and control flow

For non-bundler-friendly targets the file wraps its work in `(function(Module){ ... })(Module)`. It consumes `globalThis.sqlite3InitModuleState` from `extern-post-js.c-pp.js` or creates a diagnostic fallback, then deletes the global. It installs `Module.locateFile(path, prefix)` bound to that state. The resolver delegates to caller-provided `emscriptenLocateFile` when present, uses `new URL(path, import.meta.url).href` for ESM, or otherwise checks a URL parameter matching the resource name, `sqlite3Dir`, `scriptDir`, and finally `prefix + path`. Debug logging records the decision when `sqlite3.debugModule` is set.

When enabled by preprocessor flags, and not in wasmfs or node builds, it overrides `Module.instantiateWasm(imports, onSuccess)`. The override delegates to caller-provided `emscriptenInstantiateWasm` if present. Otherwise it resolves `sIMS.wasmFilename`, fetches it with same-origin credentials, uses `WebAssembly.instantiateStreaming()` when available, falls back to `arrayBuffer()` instantiation for older Safari, stores the instantiated metadata on `sIMS.instantiateWasm`, and calls Emscripten's `onSuccess(instance, module)`.

## State, persistence, dependencies, and risks

The primary state is initialization metadata and the installed `Module` hooks. No database persistence occurs. Dependencies include `globalThis.sqlite3InitModuleState`, `Module`, Emscripten's optional `scriptDirectory`, `fetch`, `WebAssembly.instantiateStreaming`, `import.meta.url` in ESM builds, and build-time preprocessor substitutions.

Risks include fragile resource-location heuristics, server MIME or credential issues for streaming wasm instantiation, unsupported node/bundler/wasmfs combinations, and caller override hooks being explicitly unsupported back doors that may break if Emscripten changes. Test signals include loading from a script tag, `importScripts()`/Worker contexts with `sqlite3.dir`, query-parameter overrides for the wasm filename, Safari fallback behavior, user-supplied `locateFile` and `instantiateWasm` hooks, and debug logs showing the resolved URI.
