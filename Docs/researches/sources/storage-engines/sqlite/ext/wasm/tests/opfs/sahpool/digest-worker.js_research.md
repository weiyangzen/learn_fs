# sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/digest-worker.js

## Purpose
`tests/opfs/sahpool/digest-worker.js` is a worker used by the SAHPool digest test. It verifies that the OPFS SyncAccessHandle Pool VFS can reopen and distinguish persisted databases after the `computeDigest()` fix.

## Important APIs, Types, And Functions
It defines `wPost()`, `log()`, `hasOpfs()`, and `runTests(sqlite3, poolUtil)`. `hasOpfs()` checks browser OPFS and `createSyncAccessHandle` availability. The worker imports sqlite3 from the `sqlite3.dir` URL parameter, initializes the module, installs `sqlite3.installOpfsSAHPoolVfs()` with name `opfs-sahpool-digest`, `clearOnInit: false`, and `initialCapacity: 6`, then opens databases through `poolUtil.OpfsSAHPoolDb`.

## Control Flow
The worker first aborts if OPFS SAH prerequisites are missing. It imports sqlite3, logs version, installs/acquires the named SAHPool VFS, and runs three DB operations: create/insert/close `/my.db`, reopen `/my.db` and insert again, then create/insert `/my2.db`. It logs record counts to both console and parent.

## State And Persistence Behavior
SAHPool storage is intentionally not cleared on init, so `/my.db` and `/my2.db` may persist across runs depending on pool state. The test closes each DB promptly. It does not remove the VFS or unlink files, because the digest test is concerned with persistent identity and digest behavior.

## Dependencies And Integration Points
Dependencies are Worker globals, browser OPFS SAH support, generated sqlite3 JS, and `installOpfsSAHPoolVfs`. It integrates with a parent digest test page that handles `log` and `error` messages.

## Risks And Test Signals
Risks include environment lack of SAH, stale persistent pool contents affecting counts, missing cleanup causing cross-test interference, and install failures when another worker holds the same pool. Passing signals are `vfs acquired`, successful reopen of `/my.db`, increasing counts across reopen, separate count for `/my2.db`, and no OPFS-not-detected error.
