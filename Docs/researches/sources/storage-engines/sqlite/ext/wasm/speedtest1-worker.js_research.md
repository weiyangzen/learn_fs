# sources/storage-engines/sqlite/ext/wasm/speedtest1-worker.js

## Purpose
`speedtest1-worker.js` is a classic worker wrapper for running the `speedtest1` wasm application from a browser UI. It imports the generated `speedtest1.js`, initializes the SQLite module, optionally installs the OPFS SAHPool VFS, runs `wasm_main()` with requested CLI flags, and posts structured status/log/results back to the page.

## Important APIs, Types, And Functions
`wasmfsDir(wasmUtil)` probes browser OPFS handles and calls `sqlite3_wasm_init_wasmfs('/opfs')` when available. `mPost()` posts `{type,data}` messages. `runSpeedtest(cliFlagsArray)` builds `argv`, rewrites `--vfs opfs-sahpool` to the configured real SAHPool VFS name, installs `sqlite3.installOpfsSAHPoolVfs()` when needed, invokes `App.wasm.xCall('wasm_main', ...)`, and sends `run-start`/`run-end`. `globalThis.onmessage` accepts `run`.

## Control Flow
The worker chooses the speedtest JS URL from `sqlite3.dir`, imports it, wires logging into `App.logBuffer`, initializes the Emscripten module with print/status hooks, stores `App.sqlite3`, `App.wasm`, and `App.pDir`, posts `ready`, and lists registered VFSes. Each `run` message executes one benchmark with isolated scoped allocations and reports errors through `error` messages.

## State And Persistence Behavior
The worker keeps module state in the `App` object, including cached wasm utilities, a log buffer, the persistent directory, and a cached `$SAHPoolUtil` on the sqlite3 namespace. Benchmark DB files are placed under the wasmfs OPFS mount. SAHPool installation uses a named VFS, `initialCapacity: 3`, `clearOnInit: true`, and verbosity. Scoped argv memory is popped in `finally`.

## Dependencies And Integration Points
It depends on generated `speedtest1.js`, browser Workers, Emscripten's module initialization, SQLite wasm exports, OPFS browser APIs, optional `installOpfsSAHPoolVfs`, and a UI controller that sends `run` and handles `ready`, `stdout`, `stderr`, `load-status`, `run-start`, `run-end`, and `error`.

## Risks And Test Signals
Risks include missing OPFS, stale `sqlite3.dir`, unsupported SAHPool installation, CLI flag ordering, cross-run retained SAHPool state, and long synchronous `wasm_main` calls blocking the worker. Strong test signals are `ready`, correct pointer/heap logs, successful VFS list, benchmark start/end messages, proper SAHPool rename/install logs when requested, and no unhandled worker message types.
