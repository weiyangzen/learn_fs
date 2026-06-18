# sources/storage-engines/sqlite/ext/wasm/SQLTester/SQLTester.mjs

## Purpose

This ES module is a JavaScript/WASM port of SQLite's SQLTester framework. It imports the SQLite WASM module, defines a parser and executor for SQLTester `.test` scripts, manages SQLite database handles, executes SQL through the C API, compares result buffers against expected command output, and exports a namespace used by `SQLTester.run.mjs` and other test harnesses.

## Important APIs, Classes, and Functions

The exported namespace contains `SQLTester`, `TestScript`, `Command`, `Outer`, exception classes, `Util`, and the initialized `sqlite3` object. `tryInstallVfs()` can install a registered VFS as the default, though OPFS installation is currently behind disabled conditionals. `Util` provides `unlink()`, `argvToString()`, UTF-8 encode/decode helpers, and a WASM-wrapped `sqlite3__wasm_SQLTester_strglob()` glob matcher.

`Outer` is a buffered output/logger abstraction with verbosity support. `SQLTester` owns test scripts, input and result buffers, metrics, the current null rendering, column-name output mode, database slots, default database initialization SQL, and execution helpers. `TestScript` owns byte content, parser cursor state, module/testcase metadata, directive handling, command body fetching, line decoding, and command dispatch.

Command subclasses implement SQLTester directives: `--close`, `--column-names`, `--db`, `--glob`, `--notglob`, `--open`, `--new`, `--null`, `--print`, `--result`, `--json`, `--run`, `--tableresult`, `--json-block`, `--testcase`, and `--verbosity`. `CommandDispatcher` lazily instantiates and caches command handlers by name.

## Control Flow

Module initialization awaits `sqlite3ApiInit()` from `/jswasm/sqlite3.mjs`, then prepares helper enums and classes. A caller creates `SQLTester`, adds `TestScript` instances, and calls `runTests()`. For each script, `SQLTester` resets buffers and database handles, runs the script, catches `SQLTesterException` subclasses, updates metrics, reports per-file timing and pass/fail state, then deletes the default test database.

`TestScript.run()` decodes lines from a `Uint8Array`, checks for unsupported directives, dispatches command lines beginning with `--`, and appends non-command lines to the SQL input buffer. Commands generally consume the accumulated SQL with `takeInputBuffer()`, execute it through `SQLTester.execSql()`, and compare or ignore results depending on command type.

`execSql()` prepares and steps one or more SQL statements using low-level SQLite WASM C APIs. It encodes SQL to UTF-8, allocates scoped WASM memory for statement and tail pointers, repeatedly calls `sqlite3_prepare_v3()`, steps rows, appends escaped or raw column text to the result buffer, optionally includes column names, finalizes statements, and returns the SQLite result code. Table-result commands fetch a body up to `--end` and compare each output row to a glob or JSON string.

## State and Persistence

Runtime state is held in JavaScript private fields. Database state uses up to seven SQLite handles stored in `#db.list`, with slot 0 as the default `test.db`. `reset()` clears SQL buffers, closes all databases, resets metrics for the current script, restores null output to `nil`, disables column names, and resets the current DB slot. `#setupInitialDb()` deletes and recreates `test.db` on demand. `Util.unlink()` calls `sqlite3__wasm_vfs_unlink` through WASM. No browser storage is used unless the disabled OPFS VFS block is re-enabled.

## Dependencies and Integration Points

The module depends on `/jswasm/sqlite3.mjs`, Web APIs `TextDecoder` and `TextEncoder`, SQLite WASM helpers (`wasm.xWrap`, `pstack`, `scopedAllocCall`, pointer helpers), SQLite C APIs, and the C-side helper symbols `sqlite3__wasm_vfs_unlink` and `sqlite3__wasm_SQLTester_strglob`. It integrates with `SQLTester.run.mjs`, generated `test-list.mjs`, and the broader wasm build that must export the required C symbols and JSON functionality used by the tests.

## Risks and Edge Cases

The parser rejects C-preprocessor lines, triple-dash directives, mixed module directives, unsupported required properties, and newline-pipe combinations. Required-property support is effectively disabled because `#checkRequiredProperties()` currently returns false immediately, making such directives incompatible. `currentDb(...args)` appears to reference an undefined `id` variable when setting the current DB from arguments; most command paths use `currentDbId()` instead. `ResultRowMode` defines `ONLINE`, but command code passes `ResultRowMode.ONELINE`; because `execSql()` only checks for `NEWLINE`, this still behaves as one-line output but is a naming mismatch. Output comparison only uses text values via `sqlite3_column_text()`, so binary result fidelity is not represented. Large scripts are decoded line by line and large generated test modules can increase memory pressure.

## Test Signals

`SQLTester.run.mjs` includes a sanity script that exercises most commands and then runs generated tests from `test-list.mjs`. Successful execution reports SQLite version, pointer size, per-script test counts, failures, and total time. The module also exposes detailed verbosity output for parser and SQL execution diagnostics.
