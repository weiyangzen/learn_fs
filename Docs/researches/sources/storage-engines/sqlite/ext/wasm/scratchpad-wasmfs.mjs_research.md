# sources/storage-engines/sqlite/ext/wasm/scratchpad-wasmfs.mjs

## Purpose
`scratchpad-wasmfs.mjs` is a small manual smoke test for the experimental `sqlite3-wasmfs.mjs` build. It loads the wasmfs module in the main JS thread, checks whether persistent wasmfs/OPFS storage is mounted, opens a persistent database, and inserts/tallies rows.

## Important APIs, Types, And Functions
It imports `sqlite3InitModule` from `./jswasm/sqlite3-wasmfs.mjs`. `test1(db)` creates table `t`, runs a transaction, inserts a timestamp, and logs the row count. `runTests(sqlite3)` logs module/version details, calls `capi.sqlite3_wasmfs_opfs_dir()`, opens `new sqlite3.oo1.DB(persistentDir + '/foo.db')`, runs the test list, closes the database, and reports elapsed time.

## Control Flow
Module initialization returns a promise. On success, `runTests()` reads the `capi`, `oo1`, and `wasm` namespaces, discovers the persistent directory, opens `foo.db`, runs each test function with timing banners, closes the DB in `finally`, and prints total runtime. If no persistent directory is available, it logs an error but still attempts to continue with the returned path, making this primarily a developer scratchpad.

## State And Persistence Behavior
The script persists data in `foo.db` under the wasmfs OPFS mount returned by `sqlite3_wasmfs_opfs_dir()`. Repeated runs append rows to table `t`; it does not unlink the database. All other state is transient console logging and local timing.

## Dependencies And Integration Points
It depends on a browser context with ESM support, the experimental wasmfs build artifact, SQLite's `capi` and `oo1` APIs, and browser OPFS capabilities when persistence is expected. It is not a formal harness; it integrates as a local diagnostic page/script alongside the wasm distribution.

## Risks And Test Signals
Risks include running in an environment without OPFS/wasmfs support, path concatenation after a falsey persistent directory, and persistent row counts hiding clean-run assumptions. Useful test signals are successful module load, non-empty persistent directory logging, successful `foo.db` open, monotonic `count(*)`, no leaked open DB after `finally`, and no browser console exceptions.
