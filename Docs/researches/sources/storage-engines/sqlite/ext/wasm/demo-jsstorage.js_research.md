# sources/storage-engines/sqlite/ext/wasm/demo-jsstorage.js

## Purpose

`demo-jsstorage.js` is a main-thread test/demo for SQLite WASM builds with `kvvfs` support. It exercises `sqlite3.oo1.JsStorageDb`, showing how a database can persist through browser `localStorage` or `sessionStorage`.

## Important APIs, Types, and Functions

- `runTests(sqlite3)`: initializes the module state, checks VFS support, opens a JS storage-backed database, and wires DOM controls.
- `capi.sqlite3_vfs_find()`: validates that SQLite is initialized and that the `kvvfs` VFS is available.
- `new oo.JsStorageDb(dbStorage)`: opens a DB backed by `localStorage` or `sessionStorage`.
- `db.storageSize()` and `db.clearStorage()`: report and clear storage used by the backing VFS.
- `db.exec()` and `db.selectValue()`: initialize and query the demo table.
- DOM buttons: `#btn-clear-storage`, `#btn-clear-log`, `#btn-init-db`, `#btn-select1`, and `#btn-storage-size`.

## Control Flow

After `sqlite3InitModule(globalThis.sqlite3TestModule)` resolves, `runTests()` validates `kvvfs`, chooses `local` storage by default, creates the `JsStorageDb`, and attaches button handlers. The init button drops and recreates table `t`, inserts three time-derived integers, and logs saved SQL. The select button prints sorted rows. On startup, the script checks `sqlite_master`; if the database already has schema entries it reports previous-session data and triggers a select.

## State and Persistence

The key state is the browser storage backing `kvvfs`. With the current `dbStorage = "local"` choice, data persists across page reloads and browser restarts subject to browser storage policy. Switching to `"session"` would scope data to the tab/session. The code exposes clear and size operations so test runs can reset storage.

## Dependencies and Integration Points

The script must run in the main JS thread because it uses `document`, browser storage APIs, and the `kvvfs` implementation. It requires `sqlite3.js` to be loaded before the script and requires `SqliteTestUtil` for assertions. The page must provide the expected output element and buttons.

## Risks and Edge Cases

- The script exits early if the build lacks `kvvfs`.
- Browser storage quotas, privacy modes, or disabled storage can affect persistence and storage-size results.
- The selected storage backend is hard-coded with a ternary-like `0 ? "session" : "local"` pattern, so tests may need source modification to cover session storage.
- `saveSql` and `theStore` are logged for debugging but not otherwise validated.

## Test Signals

Expected signals include successful `sqlite3_vfs_find(null)`, presence of `kvvfs`, non-throwing `JsStorageDb` construction, a meaningful `storageSize()` value, successful table initialization, repeatable select output, visible previous-session data on reload, and clear-storage reducing/removing entries.
