# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManTree.hh

Purpose: declares the manager-connection tree coordinator used to serialize and validate root versus interior manager connection attempts.

Important APIs/types/functions: `Abort()`, `Connect()`, `Disc()`, `Register()`, `Trying()`, enum `connStat`, constructor, private `TreeInfo` slots with semaphore/node/status/level, and counters for active topology state.

Control flow: callers register once, call `Trying()` before attempting a level, call `Connect()` after successful connection, and call `Disc()` after loss. Private `Pause()` and `Redrive()` implement wait/wake transitions.

State and persistence behavior: fixed-size per-process coordination table sized by `XrdCmsManager::MTMax`; no durable persistence.

Dependencies: `XrdCmsManager.hh` for `MTMax`, `XrdCmsNode` forward declaration, and pthread mutex/semaphore wrappers.

Integration points: owned by `XrdCmsManager` for each site-manager connection group and consulted by CMS protocol connection setup.

Risks: no explicit copy prevention and fixed `tmInfo` capacity. The header inlines lock-unlock behavior in `Pause()`; callers must follow the expected lock-held protocol.

Test signals: compile/API tests, status transition unit tests, and thread sanitizer tests for wait/wake paths.
