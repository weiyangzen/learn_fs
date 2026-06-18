<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_cache.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_cache.c

## Purpose
`idmapper_cache.c` implements the positive ID-mapping cache used by NFS-Ganesha to remember user-name to UID/GID mappings and group-name to GID mappings. It keeps bidirectional AVL indexes, small direct hash hints for ID lookups, FIFO expiry queues, DBus inspection hooks when enabled, and monitoring updates for hit/miss, entry-count, reaped, and evicted-entry metrics.

## Important APIs, types, and functions
- `struct cache_user` stores a `gsh_buffdesc` user name, UID, optional primary GID, two AVL nodes, a UID-tree membership flag used for GSS principals, an insertion `epoch`, and FIFO queue linkage.
- `struct cache_group` stores a group name, GID, name/GID AVL nodes, FIFO linkage, and insertion epoch.
- Global state is split by entity type: `idmapper_user_lock`, `idmapper_group_lock`, `uname_tree`, `uid_tree`, `gname_tree`, `gid_tree`, `uid_cache[]`, `gid_cache[]`, `user_fifo_queue`, and `group_fifo_queue`.
- Comparators `uname_comparator()`, `uid_comparator()`, `gname_comparator()`, and `gid_comparator()` define AVL order by `gsh_buffdesc`, UID, or GID.
- `idmapper_cache_init()`, `idmapper_cache_reap()`, `idmapper_clear_cache()`, and `idmapper_destroy_cache()` manage lifecycle.
- `idmapper_add_user()` and `idmapper_add_group()` insert or replace mappings, reconcile duplicate entries, enforce configured max counts, and update metrics.
- `idmapper_lookup_by_uname()`, `idmapper_lookup_by_uid()`, `idmapper_lookup_by_gname()`, and `idmapper_lookup_by_gid()` are the read-side lookup surface. ID lookups first consult the direct cache slot, then fall back to AVL lookup.
- DBus methods `cachemgr_show_idmapper_users` and `cachemgr_show_idmapper_groups` expose cache contents under `USE_DBUS`.

## Control flow
Initialization creates two rwlocks, initializes four AVL trees, clears direct ID hint arrays, and initializes FIFO queues. Callers are expected to hold the appropriate user or group rwlock in the mode documented by each public function.

Insertion allocates a single object containing the struct and inline name bytes, records the current time, inserts into the name tree, and handles duplicates by removing stale entries before reinserting. User insertion has special merge behavior: if the same non-expired user/UID appears through different idmapping paths, it can retain a previously known GID or UID reverse mapping. Non-GSS users are also inserted into the UID tree and direct `uid_cache` slot. Group insertion always inserts into both name and GID indexes and updates `gid_cache`.

Lookups under read lock search the relevant tree or direct ID cache. A found but expired entry is returned as a miss, leaving actual removal to the reaper or clear path. Reapers take write locks and remove expired FIFO heads until the first non-expired entry, relying on insertion-order queues and fixed validity windows. Clearing takes both user and group write locks, clears direct caches, drains AVL trees, and logs removed counts.

## State and persistence
All state is in process memory. Entry validity and eviction are driven by `nfs_param.directory_services_param` fields such as user/group time validity and max cache counts. The direct ID arrays are best-effort hints and are rebuilt by name lookup or AVL fallback; they are explicitly atomically accessed under read locks. No state is persisted across restart, and the cache content can be observed over DBus when compiled in.

## Dependencies and integration points
The file depends on Ganesha allocator/logging helpers, `gsh_buffdesc_comparator()`, `avltree`, BSD `TAILQ`, pthread rwlocks, idmapper public declarations, global `nfs_param`, atomic pointer helpers, DBus helpers, and `idmapper_monitoring`. It is called by higher-level idmapping code and complements `idmapper_negative_cache.c` for known misses.

## Risks
- Lookup functions can return false for expired entries while stale entries remain allocated until reap or clear; callers must treat false as "resolve externally" rather than "definitely absent from tree".
- The direct UID/GID cache slots are overwritten by modulo hash and cleared on removal; misuse outside the documented locks would risk stale pointers.
- `idmapper_add_user()` assumes caller-held write lock. Missing that contract can corrupt AVL trees or FIFO queues.
- User duplicate merge behavior is subtle for GSS principal versus plain NFS mappings and can regress reverse lookup behavior if simplified.
- DBus string formatting truncates names to 255 bytes for display, so DBus output is diagnostic, not a lossless export.

## Test signals
- Unit or integration tests should cover add/lookup by both directions, duplicate name/ID replacement, GSS principal mappings without UID-tree insertion, and merging of GID or reverse mapping from an existing non-expired entry.
- Cache expiry tests should verify expired lookups count as misses and later reaper calls remove only FIFO-expired heads.
- Capacity tests should exceed user and group max counts and confirm oldest entries are evicted and metrics update.
- Concurrency tests should exercise read-side direct cache fallback under the documented rwlocks.
- DBus builds should verify user/group cache listing shape and timestamped replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_cache.c -->
