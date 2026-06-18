# sources/storage-engines/sqlite/ext/wasm/tests/opfs/concurrency/worker.js

## Purpose
`tests/opfs/concurrency/worker.js` is the worker-side OPFS concurrency stress participant. Each worker opens the same database through either `OpfsDb` or `OpfsWlDb`, creates shared tables, then repeatedly writes its worker id and timestamp while retrying SQLITE_BUSY.

## Important APIs, Types, And Functions
It parses `workerId`, `opfs-unlock-asap`, `vfs`, `interval`, `iterations`, and `unlink-db` URL arguments. It imports sqlite3 from `sqlite3.dir` with a unique `opfs-async-proxy-id`, sets `sqlite3InitModule.__isUnderTest`, initializes sqlite3, and defines `wPost()`, `stdout()`, `stderr()`, `wait()`, `finish()`, `run()`, and `doWork()`.

## Control Flow
After initialization, it verifies the private `sqlite3.opfs` namespace, optionally unlinks `concurrency-tester.db`, posts `loaded`, and waits for a `run` message. `run()` chooses the DB constructor from `options.vfs`, loops on open while SQLITE_BUSY occurs, sets `sqlite3_busy_timeout`, creates tables inside `sqlite3_js_retry_busy`, then schedules interval work. Each interval inserts or replaces a row for the worker in table `t1`, using retry callbacks to log busy attempts. It finishes after `iterations` or failure.

## State And Persistence Behavior
Workers share `concurrency-tester.db` in OPFS. Each keeps its own DB handle, interval count, delay, and possible error. The DB is closed in `finish()`. Optional `opfs-unlock-asap` is propagated in the file URI to exercise lock-release behavior.

## Dependencies And Integration Points
It depends on Worker globals, generated sqlite3 JS, OPFS private test APIs, `sqlite3.oo1.OpfsDb`, `sqlite3.oo1.OpfsWlDb`, busy timeout/retry helpers, and the UI coordinator's message protocol. It requires unique async proxy ids so OPFS worker plumbing does not collide.

## Risks And Test Signals
Risks include invalid VFS names, indefinite busy-open loops under severe contention, private OPFS API changes, and missed `finish()` if asynchronous errors occur after scheduling. Good signals are `loaded`, successful constructor selection, bounded BUSY retry logs, exact requested interval count, successful close, and no `failed` messages across repeated multi-worker runs.
