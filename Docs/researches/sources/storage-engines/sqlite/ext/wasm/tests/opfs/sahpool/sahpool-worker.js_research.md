# sources/storage-engines/sqlite/ext/wasm/tests/opfs/sahpool/sahpool-worker.js

## Purpose
`tests/opfs/sahpool/sahpool-worker.js` is the worker counterpart for the SAHPool pausing demo. It imports sqlite3, optionally installs or unpauses a named SAHPool VFS, initializes/query/removes a small database, and reports each state transition to the coordinator.

## Important APIs, Types, And Functions
It parses `workerId` and `sqlite3.dir`, defines `wPost()` and `log()`, and stores `capi`, `wasm`, `S`, and `poolUtil`. `sahPoolConfig` names the VFS `opfs-sahpool-pausable` with `clearOnInit: false` and `initialCapacity: 3`. `sqlExec(sql)` opens `/my.db` with `poolUtil.OpfsSAHPoolDb`, executes SQL, returns results, and closes the DB. `onmessage` handles `vfs-acquire`, `db-init`, `db-query`, `vfs-remove`, and `vfs-pause`.

## Control Flow
The worker imports sqlite3, checks OPFS SAH prerequisites, initializes sqlite3, logs version/source id, and posts `initialized`. On `vfs-acquire`, it either installs the VFS or unpauses an existing `poolUtil`. `db-init` drops/creates/fills `mytable`. `db-query` returns ordered rows. `vfs-pause` calls `pauseVfs()` synchronously and reports paused. `vfs-remove` awaits `removeVfs()` and reports removed.

## State And Persistence Behavior
The named SAHPool VFS and `/my.db` persist inside the worker's pool utility until paused or removed. `clearOnInit: false` lets data survive across pause/unpause and between workers in the demo sequence. Each SQL operation opens and closes a short-lived DB handle, avoiding pause attempts while a DB is open.

## Dependencies And Integration Points
It depends on Worker globals, generated sqlite3 JS, OPFS SAH APIs, `installOpfsSAHPoolVfs`, and the coordinator's message protocol. It is tightly coupled to `sahpool-pausing.js` ordering and message names.

## Risks And Test Signals
Risks include missing OPFS, unhandled async rejection in VFS acquire/remove, attempting pause with open DBs if `sqlExec` changes, and stale pool state after failed runs. Passing signals are `initialized`, version log, `vfs-acquired`, `db-inited`, query result `[[11],[22],[33]]` style rows, `vfs-paused`, second-worker acquire/unpause, and final `vfs-removed`.
