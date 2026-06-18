# sources/storage-engines/sqlite/ext/wasm/api/extern-post-js.c-pp.js

## Purpose

This extern post-JS fragment runs outside Emscripten's module initialization scope after the generated `sqlite3InitModule` has been defined. Its main job is to replace Emscripten's exported initializer with SQLite's public initializer: callers still invoke `sqlite3InitModule(...)`, but the resolved value is the `sqlite3` namespace rather than the raw Emscripten `Module` in normal builds.

## Important APIs and control flow

The file captures `originalInit = sqlite3InitModule`, creates `globalThis.sqlite3InitModuleState`, and installs a wrapper function `globalThis.sqlite3InitModule = function ff(...args)`. The state object records the current script, whether the environment is a worker, `location`, URL parameters, a build-substituted `wasmFilename`, optional debug logging, and script/sqlite3 directory hints. When the wrapper is called it preserves caller-supplied `locateFile` and `instantiateWasm` hooks in `sIMS`, calls `originalInit`, then invokes `EmscriptenModule.runSQLite3PostLoadInit(sIMS, EmscriptenModule, !!ff.__isUnderTest)`. That post-load function is supplied by the post-JS header/footer constellation and performs the real SQLite API bootstrap.

For non-ESM builds it rewrites CommonJS, AMD, and plain `exports` integration points to export the wrapper. For ESM builds it assigns `toExportForESM`, replaces `sqlite3InitModule`, and exports it as the module default. A wasmfs/PThread-specific branch returns the Emscripten module when called from generated pthread workers because those workers expect the raw module argument to flow through.

## State, persistence, dependencies, and risks

The key state is transient global initialization metadata. It is intentionally stored on `globalThis` because Emscripten currently prevents attaching it directly to the generated initializer in the needed way. `pre-js.c-pp.js` consumes and deletes this state. URL parameters such as `sqlite3.debugModule` and `sqlite3.dir` influence logging and resource location, and the build system must replace `@sqlite3.wasm@` with the actual wasm filename.

Dependencies include Emscripten's generated `sqlite3InitModule`, `Module.runSQLite3PostLoadInit`, browser globals, module-system globals, and build preprocessor flags. Risks cluster around load order and bundling: if the generated initializer is missing, the file throws immediately; if current script or URL discovery fails, wasm location must fall back to `pre-js` logic or caller overrides; ESM/bundler handling is deliberately different to avoid breaking bundlers. Test signals include successful initializer replacement, correct debug-state transfer into `pre-js`, correct wasm lookup under script-tag, worker, and ESM builds, and expected return type for wasmfs pthread workers.
