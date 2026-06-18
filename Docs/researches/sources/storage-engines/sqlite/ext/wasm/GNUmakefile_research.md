# sources/storage-engines/sqlite/ext/wasm/GNUmakefile

## Purpose

This GNU makefile is SQLite's canonical JS/WASM build driver. It is aimed at SQLite project development and release packaging, not general application builds. It builds development and optimized WASM artifacts, JS API bundles, worker helper files, tester applications, speedtest builds, fiddle builds, distribution zips, testing deployments, documentation copies, and npm bundle artifacts. It assumes a Linux-like environment with GNU tools, bash, Emscripten, and optionally wabt `wasm-strip`.

## Important Targets, Variables, and Macros

Primary targets include `all`, optimization rebuild targets `o0`, `o1`, `o2`, `o3`, `os`, `oz`, release targets `dist` and `snapshot`, cleanup targets, `for-testing`, `push-testing`, `update-docs`, `httpd`, `push-fiddle`, and `npm`. Build directories are `dir.dout` for deliverables (`jswasm`) and `dir.tmp` for intermediates (`bld`). `sqlite3.c` defaults to the canonical amalgamation or SEE variant. `SQLITE_OPT.common` and `SQLITE_OPT.full-featured` define compile-time SQLite features; full builds include session, preupdate hook, FTS5, RTREE, metadata, dbstat, dbpage, bytecode, and other extensions.

Reusable build macros include `b.mkdir@`, `b.cp`, `b.c-pp.shcmd`, `b.c-pp.target`, `b.strip-js-emcc-bindings`, and `b.call.patch-export-default`. Generated build logic comes from the local `mkwasmbuilds` helper, which creates `.wasmbuilds.make` and fills in build names, output names, c-pp define sets, and many per-build rules.

Key Emscripten controls include `emcc.WASM_BIGINT`, `emcc.MEMORY64`, `emcc_opt`, `emcc_opt_full`, `emcc.jsflags`, `emcc.INITIAL_MEMORY`, `sqlite3.js.init-func`, exported function list generation, runtime method exports, imported memory, modularization, dynamic-execution disabling, table growth, stack size, and undefined symbol reporting.

## Control Flow

At startup the makefile determines whether it is cleaning. Non-clean builds require `config.make`, bash, `emcc`, and optionally `wasm-strip`. Optimized targets require `wasm-strip`; development builds warn but can continue without it. It then resolves source paths, detects SEE, chooses bare-bones or full-featured SQLite options, builds local tools such as `version-info`, `stripccomments`, `c-pp`, and `mkwasmbuilds`, and includes generated make rules.

The JS API assembly flow creates a license/version file, a JSON build-version initializer, concatenates ordered API JS components into a post-js input, preprocesses C-preprocessor-style JS sources with `c-pp`, and uses emcc pre/post JS hooks to produce module outputs. Supplementary worker/promiser/OPFS proxy files are generated separately for vanilla, ESM, and bundler-friendly forms.

Test and benchmark flow builds `speedtest1` variants and `tester1` variants covering main-thread script, worker script, ESM main thread, ESM worker, and 32/64-bit pointer modes. Fiddle flow compiles shell/fiddle-specific builds and optional jquery.terminal assets. Release flow runs distribution scripts or forces clean optimized npm builds and zips stable downstream filenames.

## State and Persistence

Persistent outputs are primarily under `ext/wasm/jswasm`, plus tester/demo/fiddle files in the wasm directory tree and distribution zip files. Intermediates live under `ext/wasm/bld` and generated local tools live in the build directory. `.wasmbuilds.make` is generated and made read-only until cleaned. `config.make` is a required configured state file and is removed by `distclean`. `clean` removes `CLEAN_FILES`, `dir.dout`, and `dir.tmp`; `distclean` also removes `DISTCLEAN_FILES`.

## Dependencies and Integration Points

The makefile integrates with the top-level SQLite tree for `sqlite3.c`, `sqlite3.h`, `shell.c`, `speedtest1.c`, `tool/version-info.c`, and `tool/stripccomments.c`. It depends on Emscripten settings semantics, wabt `wasm-strip`, bash, GNU sed/awk/grep, InfoZip, rsync/ssh for deployment, and optional local documentation or jquery.terminal checkouts. It also integrates with downstream `sqlite/sqlite-wasm` npm expectations by keeping npm filenames stable.

## Risks and Edge Cases

The file contains several explicit fragility points: Emscripten minification can break exported WASM names unless `-g3` plus `wasm-strip` are used; `b.strip-js-emcc-bindings` relies on generated JS text patterns; `b.call.patch-export-default` works around Emscripten ESM default export behavior; ordering around `.wasmbuilds.make` is fragile; high optimization levels are slow; `STRICT_JS` and `STRICT` are disabled or avoided due to Emscripten issues; missing `wasm-strip` makes optimized release-quality builds unusable. Bare-bones builds intentionally remove features including session support. Custom `sqlite3.c` paths must not contain spaces.

## Test Signals

The build produces the `tester1` suite, worker tester pages, speedtest builds, `for-testing` deployment bundle, fiddle debug builds, and npm bundle zip listing. Full-featured WASM builds define `SQLITE_ENABLE_SESSION` and `SQLITE_ENABLE_PREUPDATE_HOOK`, connecting this build file to the session header and Tcl test surface. Build success across `all`, `for-testing`, `dist`, and `npm` is the primary signal, while browser execution of tester pages validates runtime behavior.
