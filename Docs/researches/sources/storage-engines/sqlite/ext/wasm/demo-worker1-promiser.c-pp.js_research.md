# sources/storage-engines/sqlite/ext/wasm/demo-worker1-promiser.c-pp.js

## Purpose

`demo-worker1-promiser.c-pp.js` demonstrates the Promise-based `sqlite3` Worker API #1 promiser wrapper. It exercises worker message types through `await` and promise chaining instead of manually managing `postMessage()` response queues.

## Important APIs, Types, and Functions

- `promiserFactory`: imported as an ES module in module builds or read from `globalThis.sqlite3Worker1Promiser.v2` in non-module builds.
- `promiserConfig`: configures optional `onready`, debug routing, `onunhandled`, and `onerror`.
- `workerPromise`: the resolved promiser function used to send worker commands.
- `wtest(msgType, msgArgs, callback)`: helper that sends a worker request and optionally validates the result.
- Worker message types: `config-get`, `open`, `exec`, `export`, and `close`.
- Test utilities: `globalThis.SqliteTestUtil` assertion counter and `sqlite3TestModule.setStatus(null)` for hiding loading UI.

## Control Flow

The script awaits `promiserFactory(promiserConfig)`, hides the loading spinner, then starts `runTests()`. It first requests `config-get` and records whether BigInt support is enabled. It opens `/testing2.sqlite3`, records the returned `dbId` into `promiserConfig`, then runs a sequence of `exec()` tests that create data, query in array/object/scalar row modes, intentionally trigger a SQL error, receive callback rows from the worker, test multi-statement result selection, delete rows, count rows, export the database, and close it twice.

The helper `wtest()` supports both `{type,args}` call style and the older two-argument style behind a disabled branch. Every callback validation is chained through promises, and many validations call `testCount()` in `finally`.

## State and Persistence

The database is worker-owned and identified by the `dbId` returned from `open`. The demo uses `/testing2.sqlite3`, then closes it at the end. It transfers data back during `export` as a `Uint8Array`, but it does not persist exported data in browser storage. The promiser config retains `dbId` after open so subsequent calls target the same DB.

## Dependencies and Integration Points

The code depends on the generated worker promiser artifact under `jswasm/`, `SqliteTestUtil`, DOM element `#test-output`, and `sqlite3TestModule`. It tests the higher-level wrapper around `sqlite3-worker1.js`, so it is an integration test between the main UI thread, worker message protocol, SQLite OO API running in the worker, and structured-clone transfer of result data.

## Risks and Edge Cases

- The source is preprocessed by `c-pp`; ES module and non-module branches differ. A build-mode mismatch can break the import/global path.
- The test expects `lastInsertRowId` to be a BigInt and adapts `changeCount` checks based on worker config.
- Callback row tests rely on end-of-result-set notifications with `rowNumber === null`.
- `promiserConfig.dbId` is mutated after open. Concurrent tests sharing that config could target the wrong DB.
- The intentional SQL error must reject the promise without breaking later worker requests.

## Test Signals

Strong signals include successful promiser initialization, `config-get` returning a boolean `bigIntEnabled`, `open` returning `dbId`, `messageId`, and VFS name, correct insert/change/last-row-id metadata, expected query rows and column names, caught intentional error, callback row counters reaching expected values, exported byte array larger than a minimal SQLite database, correct MIME type, and idempotent close behavior where the second close lacks a filename.
