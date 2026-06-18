# sources/storage-engines/sqlite/ext/wasm/test-opfs-vfs.js

## Purpose
`test-opfs-vfs.js` is a browser worker-style testing ground for SQLite's OPFS VFS. It loads `jswasm/sqlite3.js`, opens an OPFS database, verifies persistence, exercises basic transactions, and sanity-checks internal OPFS utility helpers.

## Important APIs, Types, And Functions
The main function is `tryOpfsVfs(sqlite3)`. It checks `sqlite3.opfs`, finds the `opfs` VFS via `sqlite3_vfs_find`, wraps it as `sqlite3_vfs`, optionally unlinks the DB when URL parameter `delete` is present, opens `new sqlite3.oo1.OpfsDb(dbFile,'ct')`, executes table setup/inserts, and uses `sqlite3.opfs` utilities: `unlink`, `entryExists`, `randomFilename`, `mkdir`, and recursive unlink.

## Control Flow
The script imports the generated sqlite3 loader with `importScripts()`, initializes the module, then calls `tryOpfsVfs()`. The test deletes the database only when requested, checks for existing persistent content, performs a transaction inserting three timestamp-derived values, logs row count, runs OPFS utility filesystem checks under a random temporary directory, and closes the DB in `finally`.

## State And Persistence Behavior
The database `my-persistent.db` persists in OPFS across runs unless `?delete` is supplied. Temporary OPFS directories named `/sqlite3-opfs-<random>` are created and removed during utility checks. The test uses SQLite transactions for table writes and explicitly closes the database.

## Dependencies And Integration Points
It depends on Worker globals, `importScripts`, `jswasm/sqlite3.js`, OPFS-capable browser APIs, the private `sqlite3.opfs` namespace retained for tests, and `sqlite3.oo1.OpfsDb`. It integrates as a standalone manual test page/worker for the OPFS VFS.

## Risks And Test Signals
Risks include relying on private `sqlite3.opfs` APIs, browser OPFS availability and permissions, stale persistent DB content, and cleanup failures in nested directory deletion. Passing signals are an `opfs` VFS pointer, successful `OpfsDb` open, persistent schema count on second run, increasing row count, successful mkdir/idempotent mkdir, failed unlink of non-empty directory, successful recursive cleanup, and no unclosed DB.
