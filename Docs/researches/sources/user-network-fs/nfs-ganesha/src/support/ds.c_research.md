<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/ds.c -->
# sources/user-network-fs/nfs-ganesha/src/support/ds.c

## Purpose
`ds.c` parses and manages pNFS data server (DS) configuration blocks. It stores active `fsal_pnfs_ds` records by configured server id, coordinates FSAL DS creation, and removes DS records during export or daemon cleanup.

## Important APIs, Types, and Functions
The central store is `static struct server_by_id`, with rwlock, AVL tree, and a 193-slot front cache; `dslist` tracks active DS entries. Public management APIs are `pnfs_ds_alloc`, `pnfs_ds_free`, `pnfs_ds_insert`, `pnfs_ds_get`, `pnfs_ds_put`, `pnfs_ds_remove`, `remove_all_dss`, `ReadDataServers`, `ds_cleanup`, and `server_pkginit`. Config callbacks include `fsal_cfg_commit`, `pds_init`, `pds_commit`, and `pds_display`.

## Control Flow
`server_pkginit` initializes the lock, AVL tree, list, cache, and cleanup hook. Config parsing uses `pds_block`: `pds_init` allocates a DS record, `fsal_cfg_commit` loads/initializes the named FSAL and calls its `create_fsal_pnfs_ds` method, and `pds_commit` rejects duplicate `Number` values before inserting. `pnfs_ds_insert` adds the node to the AVL tree and list, updates the cache, takes the table reference, and pins a related MDS export if present. `pnfs_ds_get` checks cache then AVL under read lock and increments the DS refcount. `pnfs_ds_remove` removes the DS from cache/tree/list, releases any related export through an op context, drops table and FSAL-created references, and lets `pnfs_ds_put` finalize resources on the last reference.

## State and Persistence Behavior
State is runtime-only: active DS objects, refcounts, AVL/cache/list membership, FSAL references, and optional MDS export references. The source of truth for persistence is the parsed NFS-Ganesha config, not this module.

## Dependencies and Integration Points
The module depends on config parsing, FSAL module loading, pNFS utility types, export reference management, op-context helpers, glist/AVL utilities, pthread locks, atomics, and logging. It integrates with pNFS file handles carrying `id_servers`, FSAL-specific DS initialization, and export lifecycle cleanup.

## Risks and Test Signals
Risks include delicate two-reference lifetime semantics, special static `special_ds` behavior for no-config paths, needing `Client`/`FSAL` config blocks last as documented, cache invalidation on removal, and possible leaks if FSAL creation partially succeeds. Test signals include duplicate DS id rejection, successful FSAL DS creation for supported FSALs, lookup cache hit/miss behavior, remove while references are held, export reference release, `remove_all_dss` at shutdown, and config-error paths for missing or invalid FSAL names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/ds.c -->
