# sources/storage-engines/sqlite/ext/wasm/speedtest1-wasmfs.mjs

## Purpose
`speedtest1-wasmfs.mjs` runs the native SQLite `speedtest1` wasm build against the experimental wasmfs OPFS mount. It is meant for browser/worker-style benchmarking of persistent storage and forwards log/error messages to the parent via `postMessage()`.

## Important APIs, Types, And Functions
It imports `sqlite3InitModule` from `./jswasm/sqlite3-wasmfs.mjs`. `wMsg()`, `log()`, and `logErr()` wrap parent messages. `wasmfsDir(wasmUtil, dirName='/opfs')` caches OPFS availability and calls `sqlite3__wasm_init_wasmfs`. `runTests(sqlite3)` wraps `sqlite3__wasm_vfs_unlink`, builds speedtest argv from URL `flags`, removes any supplied `--vfs`, adds default flags when no URL flags exist, appends `--big-transactions` and a persistent DB filename, then invokes `wasm_main`.

## Control Flow
After module initialization with print hooks, `runTests()` checks the wasmfs OPFS directory. If unavailable, it reports an error and exits. Otherwise it prepares argv, unlinks the benchmark DB before and after execution, logs warnings about long runtime, and invokes `wasm.xCall('wasm_main', argc, argv)` inside a short `setTimeout()` so initial messages reach the UI before the synchronous benchmark begins.

## State And Persistence Behavior
The benchmark database is `/opfs/speedtest1.db` when persistence is available. The script intentionally unlinks the file before execution and again after completion to keep benchmark runs isolated. Scoped WASM allocations for argv are pushed before building arguments and popped after `wasm_main()` returns.

## Dependencies And Integration Points
It depends on the wasmfs build exporting `sqlite3__wasm_init_wasmfs`, `sqlite3__wasm_vfs_unlink`, and `wasm_main`, browser OPFS interfaces, URL query parameters, and a parent page that understands `log` and `logErr` message types. It integrates with SQLite's speedtest1 wasm Make target and browser benchmarking pages.

## Risks And Test Signals
Risks include symbol-name drift (`sqlite3__wasm_init_wasmfs` versus older spellings), blocking the browser during `wasm_main`, URL flags overriding benchmark comparability, `--memdb` making the DB filename irrelevant, and cleanup failures masking persistence bugs. Good signals are successful persistent mount logging, clean DB unlinking, expected speedtest stdout/stderr, correct argv in logs, scoped allocation cleanup, and no leftover DB file after completion.
