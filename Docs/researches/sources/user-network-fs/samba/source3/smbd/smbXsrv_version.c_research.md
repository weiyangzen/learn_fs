# sources/user-network-fs/samba/source3/smbd/smbXsrv_version.c

## Purpose
Maintains a cluster-visible version gate for smbd internal `smbXsrv_*_global` record formats. It prevents nodes with incompatible supported structure versions from concurrently reading and writing volatile internal databases.

## Important APIs, Types, and Functions
`smbXsrv_version_global_init(const struct server_id *server_id)` opens `smbXsrv_version_global.tdb`, validates existing version records, filters dead nodes, records the local node's min/max/current version, stores the updated NDR blob, and caches the current version. `smbXsrv_version_global_current()` returns that cached version for session and tcon global stores.

## Control Flow
Initialization opens the TDB with `TDB_CLEAR_IF_FIRST` and incompatible hash flags, locks the fixed key `smbXsrv_version_global`, creates an empty version object if missing, or parses and validates an existing object. Each live node must advertise a range containing the global blob version; otherwise startup fails with corruption or revision mismatch. The local node entry is found by VNN or appended, then the record sequence number is incremented and stored.

## State and Persistence
State lives in volatile lock-path TDB and is cached process-wide in `smbXsrv_version_global_db_ctx` and `smbXsrv_version_global_current_version`. The global record stores node server IDs and version ranges; dead server IDs are pruned during init.

## Dependencies and Integration Points
Depends on dbwrap, TDB, generated NDR `smbXsrv_version_globalB`, serverid liveness, and lock-path helpers. Session and tcon stores call `smbXsrv_version_global_current()` to stamp their record version.

## Risks
Passing a null or stale `server_id` would undermine the node compatibility gate. If version init is skipped before session/tcon stores, `UINT32_MAX` could leak as the current version. Strict failure on range mismatch protects data but can block startup during rolling upgrades unless migration glue is added.

## Test Signals
Test first-node initialization, restart with existing compatible records, pruning dead nodes, rejection of min/max ranges that exclude current version, malformed NDR blobs, unsupported blob versions, and use of the cached version in session/tcon stores.
