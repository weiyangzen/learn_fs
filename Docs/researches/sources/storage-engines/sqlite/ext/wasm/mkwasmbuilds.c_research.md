# sources/storage-engines/sqlite/ext/wasm/mkwasmbuilds.c

## Purpose
`mkwasmbuilds.c` is a Makefile-fragment generator for SQLite's canonical wasm build. It exists to keep complex generated GNU Make rules maintainable: instead of heavy `$(eval ...)` string construction inside Make, this C program emits the rules for library, speedtest, wasmfs, node, bundler, 64-bit, and fiddle builds.

## Important APIs, Types, And Functions
The central type is `BuildDef`, with base name, emoji log tag, wasm filename substitution target, c-pp defines, emcc flags, extra dependencies, environment, optional Make `ifeq`, and `BuildDefFlags`. `BuildDefs_map` enumerates `vanilla`, `vanilla64`, `esm`, `esm64`, `bundler`, `bundler64`, `speedtest1`, `speedtest164`, `node`, `node64`, and `wasmfs`. Important emitters are `mk_prologue()`, `mk_pre_post()`, `emit_compile_start()`, `emit_logtag()`, `emit_api_js()`, `mk_lib_mode()`, `emit_gz()`, `mk_fiddle()`, and `main()`.

## Control Flow
With no arguments, `main()` emits a prologue, rules for every build in `BuildDefs_map`, and fiddle rules. With arguments, it emits only named build sections, plus `prologue` if requested, and reports unknown names to stderr. `mk_prologue()` emits sanity checks for required Make variables, wasm-strip and wasm-opt helper macros, and common emcc command macros. `mk_lib_mode()` emits one complete build rule: output path variables, c-pp defines, environment, generated API JS, pre/post JS inputs, emcc invocation, importScripts regression guard, ESM export patching, wasm stripping/optimization, JS binding stripping, deliverable copy rules, alias targets, and all/more target membership. `mk_fiddle()` emits normal and debug fiddle builds and gzip rules.

## State And Persistence Behavior
The program itself only writes Makefile text to stdout and errors to stderr. The emitted Makefile rules create per-build output directories, generated pre/post JS files, JS API bundles, JS/MJS/WASM outputs, copied deliverables, gzip files, and optional patched JS references. Build selection state is encoded in flags such as `CP_JS`, `CP_WASM`, `F_ESM`, `F_64BIT`, `F_UNSUPPORTED`, `F_NODEJS`, and `F_WASMFS`.

## Dependencies And Integration Points
Compile-time dependencies are standard C headers and the Makefile variables/functions referenced in emitted text. Runtime integration assumes Emscripten, `c-pp-lite`, wasm-strip, optional wasm-opt, generated SQLite API sources, sqlite3 wasm C input, speedtest inputs, fiddle inputs, and Make helpers such as `b.c-pp.target`, `b.cp`, `b.mkdir@`, and `b.call.patch-export-default`.

## Risks And Test Signals
Risks center on emitted Make syntax, duplicated or missing dependencies, JS/WASM filename substitution, unsupported builds silently diverging, and Emscripten behavior changes. The code has a specific guard against reintroducing `importScripts()` into ESM/bundler outputs. Validation should compile the generator, regenerate the Makefile fragment, diff expected rules, run representative `b-vanilla`, `b-esm`, `b-speedtest1`, `b-fiddle`, and optional `wasmfs`/64-bit targets, and verify copied deliverables load in browser and worker contexts.
