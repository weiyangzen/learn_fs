# sources/storage-engines/sqlite/ext/wasm/fiddle/fiddle-worker.js

## Purpose

`fiddle-worker.js` is the worker-side controller for the SQLite WASM fiddle app. It loads the fiddle WASM module, runs the SQLite shell entry point, exposes shell execution to the main thread, and handles database reset, interrupt, export, and uploaded database open requests.

## Important APIs, Types, and Functions

- `wMsg(type, data, transferables)`: posts structured `{type,data}` messages back to the UI.
- `stdout()` and `stderr()`: route shell/module output to worker messages.
- `self.onerror`: detects fatal Emscripten `ExitStatus`, marks the module dead, and reports errors.
- `Sqlite3Shell.dbFilename()`, `dbHandle()`, `dbIsOpfs()`: wrappers around exported C helpers.
- `Sqlite3Shell.runMain()`: initializes the shell by calling `sqlite3_shutdown()`, building argv, and invoking `fiddle_main(argc, argv)`.
- `Sqlite3Shell.exec(sql)`: runs shell input through exported `fiddle_exec`, emits `working` start/end, and posts `wasm-info`.
- `Sqlite3Shell.resetDb()` and `interrupt()`: wrappers around exported reset/interrupt helpers.
- `self.onmessage`: dispatches `shellExec`, `db-reset`, `interrupt`, `db-export`, and `open`.
- `fiddleModule`: Emscripten module config with `print`, `printErr`, and `setStatus`.

## Control Flow

On load, the worker defines the message protocol and imports `fiddle-module.js` with the current query string. It calls `sqlite3InitModule(fiddleModule)`, stores the resolved `sqlite3` object globally for debugging, wires a filesystem unlink helper, and posts `fiddle-ready`.

The first shell execution lazily calls `runMain()`, which initializes the shell against `/fiddle.sqlite3` and posts version and welcome messages. Each subsequent `shellExec` runs through `fiddle_exec` unless the module is dead or another command is already running. After every command it posts heap/prompt info.

Database export fetches the current DB filename and handle, calls `sqlite3_js_db_export()`, and transfers the resulting `ArrayBuffer` to the main thread. Database open accepts an uploaded `ArrayBuffer` or `Uint8Array`, forces bytes 18 and 19 to `1` to disable WAL mode, sanitizes the filename, writes the file into the Emscripten FS, opens it through the shell, and unlinks the old file where possible.

## State and Persistence

State is worker-local: `sqlite3`, `fiddleModule.isDead`, cached `xWrap()` functions, shell argv, current shell DB, Emscripten virtual filesystem files, and transient `_running` flags. OPFS can provide persistent DB storage when opened with the OPFS VFS from the shell, but upload/export paths explicitly warn that OPFS-over-VFS has limitations. Uploaded DBs are copied into the virtual filesystem.

## Dependencies and Integration Points

The worker depends on generated `fiddle-module.js`, `sqlite3InitModule`, exported C symbols such as `fiddle_main`, `fiddle_exec`, `fiddle_db_filename`, `fiddle_db_handle`, `fiddle_reset_db`, and `fiddle_interrupt`, plus SQLite JS helpers such as `sqlite3_js_db_export()` and `sqlite3_js_db_uses_vfs()`. It integrates with the main-thread `fiddle.js` message handlers through message types documented at the top of the file.

## Risks and Edge Cases

- Interrupt cannot be effective while the worker is busy because the same worker event loop must receive the interrupt message.
- The upload path can temporarily hold both old and new DB files, risking quota failures.
- Forcing bytes 18 and 19 out of WAL mode is pragmatic but assumes the uploaded file is a SQLite database and mutable.
- Filename sanitization strips directories and replaces quotes/whitespace, but all opened files are still user-controlled content.
- There is a declared but unused `dbVfs` wrapper after initialization.
- OPFS limitations are surfaced as warnings but not fully prevented by the UI.

## Test Signals

Useful tests should observe `module` status messages, `fiddle-ready`, `sqlite-version`, shell stdout/stderr, `working` start/end around each command, `wasm-info` prompt/heap updates, successful `.help` or SQL execution, export with transferable buffer and SQLite MIME handling on the UI side, uploaded DB replacement, reset output, and fatal `ExitStatus` behavior.
