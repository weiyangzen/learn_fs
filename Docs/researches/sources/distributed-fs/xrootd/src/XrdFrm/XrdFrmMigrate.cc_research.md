## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMigrate.cc

Purpose: implements the automatic migration scanner. It periodically walks configured paths, selects files that changed since the last copy time, waits for idle files to age past `Config.IdleHold`, and queues internal migration requests into `XrdFrmXfrQueue`.

Important APIs and control flow: `Migrate(1)` starts a detached migration scan thread; `Migrate(0)` runs the infinite loop. Each cycle calls `Scan()`, then repeatedly calls `Advance()` to reprocess deferred files until the wait budget expires. `Scan()` constructs `XrdFrmFiles` with recursion, compressed directories, and manual deletion, then screens filesets and sends eligible ones through `Add()`. `Eligible()` rejects missing copy time, unchanged files, and recent fail files. `Queue()` converts a fileset into an `XrdFrcRequest` with `Migrate` option, internal ID, logical path, and `migQ`.

State and persistence: migration state is mostly derived from base file mtime and persisted copy-time metadata (`cpyInfo`, lock-file mtime, or xattr). Fail files persist transfer retry suppression. `fsDefer` is an in-memory sorted linked list by base mtime; it is discarded after each cycle.

Dependencies and integration: depends on `XrdFrmFiles`, `XrdFrmTransfer::checkFF()`, `XrdFrmXfrQueue::Add()`, global `Config.pathList`, and the transfer daemon started by `XrdFrmXfrDaemon`. It logs through `Say`/trace macros.

Risks and test signals: `nowT` in `Scan()` is static-initialized, so the bad-file purge interval check may not observe time progression as intended. Queue request IDs use a static incrementing int without persistence. Tests should cover idle deferral ordering, fail-file hold behavior, logical path failures, unchanged-file suppression, and background thread startup errors.
