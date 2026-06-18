# sources/user-network-fs/nfs-ganesha/src/support/export_mgr.c

## Purpose
`export_mgr.c` is the runtime registry and administrative surface for NFS-Ganesha exports. It owns the export-id index, global export list, mount and unexport work queues, export reference lifetime, shutdown pruning, optional DBus export/stat methods, and the asynchronous delegation-transition helper used after export configuration changes. It is the bridge between parsed export configuration, PseudoFS mount/unmount operations, FSAL export lifetime, server statistics, and external management via DBus.

## Important APIs, Types, And Functions
The central state is `static struct export_by_id export_by_id`, which contains `eid_lock`, an AVL tree keyed by `gsh_export.export_id`, and a fixed-size atomic front-end cache. `exportlist`, `mount_work`, and `unexport_work` are global `glist_head` lists. The header exposes `struct gsh_export`, `EXPORT_ADMIN_LOCK`, `EXPORT_ADMIN_UNLOCK`, the advisory `export_admin_counter` seqlock, and `export_ready()`.

Key lifecycle APIs:

- `alloc_export()` allocates an `export_stats` container, initializes embedded `gsh_export` lists and lock, and starts `refcnt` at 1.
- `insert_gsh_export()` inserts into the AVL tree, takes the sentinel reference, updates the cache, and links into `exportlist`.
- `export_revert()` undoes a failed commit after insertion, removes cache/tree/list/work links, removes pNFS data-server state if present, and releases the sentinel through op-context cleanup.
- `_get_gsh_export_ref()` and `_put_gsh_export()` implement atomic reference counting and final cleanup through `free_export_resources()`, `server_stats_free()`, lock destruction, and freeing the `export_stats` container.
- `remove_gsh_export()` removes the export from the cache/tree/list, marks it `EXPORT_STALE`, removes pNFS data-server state, and drops the sentinel reference.

Lookup and iteration APIs:

- `get_gsh_export()` looks up by id through the cache first, then the AVL tree, and returns a referenced export.
- `get_gsh_export_by_path_locked()`, `get_gsh_export_by_pseudo_locked()`, and their unlocked wrappers perform longest-prefix or exact lookup over `exportlist`.
- `get_gsh_export_by_tag()` searches `FS_tag`.
- `foreach_gsh_export()` iterates `exportlist` under `eid_lock` in read or write mode.

Administrative and integration APIs:

- `mount_gsh_export()` and `unmount_gsh_export()` establish an NFSv4 op context and call `pseudo_mount_export()` or `pseudo_unmount_export_tree()`.
- `remove_all_exports()`, `prune_defunct_exports()`, `process_unexports()`, and `remove_one_export()` drive orderly shutdown and config-reread pruning.
- `export_pkginit()` initializes the manager and registers cleanup; `export_mgr_cleanup()` destroys global locks.
- `add_export_id()` and `is_export_id_match()` support config parsing of export-id lists.
- `async_deleg_transition_handler()` submits `queue_deleg_transition_handler()` to a fridge thread for delegation recall after runtime delegation policy changes.
- Under `USE_DBUS`, `dbus_export_init()` registers `org.ganesha.nfsd.exportmgr` and `org.ganesha.nfsd.exportstats` methods for dynamic add/update/remove, display, and statistics.

## Control Flow
Normal export creation starts in `exports.c`, but commits eventually call `insert_gsh_export()`. The inserted export becomes searchable by id and list traversal. Initial exports are queued on `mount_work`; dynamic add paths usually initialize the export root and mount immediately before insertion. Consumers call `get_gsh_export*()` to obtain a referenced export and later release it with `put_gsh_export()`.

Removal is staged. `remove_all_exports()` obtains the pseudo-root export, unmounts the whole PseudoFS tree, queues all exports on `unexport_work`, and drains that queue with `process_unexports()`. Each queued export is referenced, installed in `op_ctx`, and passed to `release_export()`, which eventually calls back into `remove_gsh_export()`. Config reread uses `prune_defunct_exports(generation)` to queue only exports whose `config_gen` is older than the new parse generation.

DBus add/update paths parse a provided config file and expression, collect parser errors into an `open_memstream()`, call `load_config_from_node()` with `add_export_param` or `update_export_param`, and return a string summary or DBus error. DBus remove validates id, rejects export 0 and exports with submounts, initializes an op context, and calls `release_export()`. DBus stats methods look up exports, validate whether the relevant stats block exists, emit status replies, and call the appropriate `server_dbus_*` helpers.

The delegation transition worker first takes and releases `EXPORT_ADMIN_LOCK()` to serialize behind any active export admin operation, builds an op context for the export, walks `exp_state_list`, filters `STATE_TYPE_DELEG`, derives the client address, calls `export_check_access()` for current effective permissions, and recalls read or write delegations whose permissions were disabled.

## State And Persistence Behavior
All state is in memory. Export identity is persisted only through the live AVL/list registry and configuration reload generation. The cache is a process-local acceleration structure and is invalidated on removal/revert when it points at the removed node. The sentinel reference taken during insertion keeps an export alive while it is in the manager; removal drops that sentinel and final freeing waits for all outstanding references.

`export_admin_mutex` serializes high-level add, remove, reread, and shutdown operations. `export_admin_counter` is incremented before and after such operations so other code can detect likely races. `export_by_id.eid_lock` protects the AVL tree, cache coherency, and export list iteration. Individual export contents are protected by `gsh_export.exp_lock` where needed. Path strings use `gsh_refstr` plus RCU access in temporary path helpers.

Stats timestamps (`nfs_stats_time`, `fsal_stats_time`, `v3_full_stats_time`, `v4_full_stats_time`, `auth_stats_time`, and `clnt_allops_stats_time`) track when counters were initialized or enabled. DBus enable/disable methods mutate `nfs_param.core_param` flags at runtime and reset or timestamp stats.

## Dependencies And Integration Points
This file depends on the FSAL layer, MDCACHE/stat helpers, PseudoFS helpers, NFS op-context setup, pNFS data-server cleanup, state/delegation recall, DBus, config parsing, client/IP display helpers, atomics, AVL trees, glists, pthread locks, and RCU-safe refstrings. It is tightly coupled to `exports.c` for config commits and `export_mgr.h` for the `gsh_export` structure and admin lock protocol.

Integration points to watch include `pseudo_mount_export()`, `pseudo_unmount_export_tree()`, `release_export()`, `free_export_resources()`, `server_dbus_*`, `mdcache_dbus_show()`, `fd_usage_summarize_dbus()`, `async_delegrecall_per_state()`, and `general_fridge`.

## Risks And Edge Cases
`get_gsh_export_by_path_locked()` appears to leak a `gsh_refstr` on non-exact prefix matches: it stores `ret_exp` and `len_ret` but does not release `ref_fullpath` before continuing unless it breaks on exact match. The pseudo-path variant has a bottom-of-loop `gsh_refstr_put()`, so path lookup should be reviewed specifically.

The mount and unexport work-list helpers do not take locks themselves; callers must honor the documented export-admin locking discipline. Misuse can corrupt list links because `exp_work` is a single embedded list node.

The DBus stats enable/disable methods accept known strings but do not visibly reject unknown `stat_type` values after parsing; an unknown value can return an OK status with no state change.

`async_deleg_transition_handler()` queues a raw `gsh_export *`. Correctness depends on caller-side lifetime guarantees while the fridge job is pending. The worker serializes against admin updates but does not take its own export reference before queueing.

DBus client display preserves legacy CIDR fields by appending byte fields rather than full byte arrays; callers relying on these fields should be treated as compatibility-sensitive.

## Test Signals
Useful validation includes unit or integration coverage for duplicate export IDs, cache hit and cache invalidation on remove/revert, lookup by path and pseudo with trailing slashes and prefix collisions, all mount/unexport work queue paths, config reread pruning by generation, DBus add/update/remove error reporting, stats enable/disable/status behavior, and delegation recall after disabling read/write delegation options. Leak detection around path lookup and sanitizer runs through dynamic add/update/remove are especially relevant.
