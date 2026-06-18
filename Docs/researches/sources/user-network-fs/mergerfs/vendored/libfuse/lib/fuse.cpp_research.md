# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse.cpp

## Purpose
`fuse.cpp` is mergerfs' high-level FUSE adapter. It keeps the in-memory node namespace, translates kernel low-level requests into `fuse_operations` path/file-handle callbacks, maintains lookup/open/reference state, formats directory data through `fuse_dirents_t`, and wires the high-level operation table into the low-level dispatch layer.

## Important APIs, Types, and Functions
The central static `struct fuse f` holds the single active session, operation table, name/id hash tables, node id generator, global mutex, and path lock queue. `node_table`, `nodeid_gen_t`, `lock_queue_element`, and `fuse_dh` support node lookup, path locking, and directory-handle caching. Public entry points include `fuse_new`, `fuse_destroy`, `fuse_get_session`, `fuse_exit`, `fuse_exited`, `fuse_notify_poll`, `fuse_invalidate_all_nodes`, `fuse_gc`, `fuse_gc1`, `fuse_populate_maintenance_thread`, `fuse_passthrough_open`, and `fuse_passthrough_close`.

## Control Flow
`fuse_new` copies the caller's `fuse_operations`, creates a low-level session with `fuse_path_ops`, initializes hash tables, and installs root node id `FUSE_ROOT_ID`. Low-level requests enter one of the `fuse_lib_*` handlers, resolve node ids to relative paths with `get_path*`, call the corresponding high-level operation, update node/cache state when needed, and reply through `fuse_reply_*`. Mutating operations such as unlink, rmdir, and rename use write path locks and update name-table membership. Create/tmpfile allocate provisional nodes to provide a node id to passthrough-aware backends, then either remember/open the node after success or forget it on failure.

## State and Persistence
All node state is process-local. The id/name hash tables track node ids, parents, names, lookup counts, open counts, remembered status, and `stat_crc32b`. Nothing is persisted across process restart. `remember_nodes` can pin lookups. `open_auto_cache` compares stat fingerprints and sets `keep_cache` when a file is unchanged across opens. Maintenance jobs periodically GC pooled nodes/message buffers and optionally append metrics under `/tmp/mergerfs.<pid>.info`.

## Dependencies and Integration Points
This file integrates with `fuse_lowlevel.cpp` through `fuse_path_ops`, with `node.cpp`/`node.hpp` for pooled `node_t`, with `fuse_dirents.cpp` for readdir buffers, with `fuse_msgbuf.cpp` for read buffers, with `fuse_req.cpp` for request allocation, with `fuse_cfg` for runtime policy, and with kernel passthrough ioctls on `/dev/fuse`.

## Risks
The file is concurrency sensitive: path locks, node refcounts, `open_count`, and queued condition variables must stay balanced. Incorrect node unlink/rename ordering can produce stale paths or use-after-free. `find_node` provisional nodes need cleanup on every failed create/tmpfile path. `free_path_and_update_stat` must not update a node after kernel forget. Directory handles rely on a lock barrier before destruction.

## Test Signals
Exercise lookup/forget churn, open-unlink-release, rename over existing nodes, interrupted create/open replies, readdir/readdirplus with repeated offsets, auto-cache invalidation after stat changes, passthrough open/close failure paths, and maintenance GC under active operations. Race tests should stress parallel read/process threads with unlink, rename, forget, and releasedir.
