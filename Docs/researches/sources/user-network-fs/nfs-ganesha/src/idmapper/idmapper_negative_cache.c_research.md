<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_negative_cache.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_negative_cache.c

## Purpose
`idmapper_negative_cache.c` implements a negative cache for idmapping misses. It stores failed user-name, group-name, and UID resolutions so repeated lookups avoid expensive external resolver calls until a configured timeout expires.

## Important APIs, types, and functions
- `negative_cache_entity_type_t` distinguishes `USERNAME`, `GROUP`, and `UID`.
- `negative_cache_entity_t` stores either a name `gsh_buffdesc` or UID, one AVL node, insertion epoch, FIFO queue linkage, and inline name bytes.
- Separate global locks protect each cache: `idmapper_negative_cache_user_lock`, `idmapper_negative_cache_group_lock`, and `idmapper_negative_cache_uid_lock`.
- Separate AVL trees and FIFO queues back name and UID caches: `uname_tree`, `gname_tree`, `uid_tree`, `negative_user_fifo_queue`, `negative_group_fifo_queue`, and `negative_uid_fifo_queue`.
- `idmapper_negative_cache_init()`, `idmapper_negative_cache_reap()`, `idmapper_negative_cache_clear()`, and `idmapper_negative_cache_destroy()` manage lifecycle.
- Add APIs are `idmapper_negative_cache_add_user_by_uid()`, `idmapper_negative_cache_add_user_by_name()`, and `idmapper_negative_cache_add_group_by_name()`.
- Lookup APIs are `idmapper_negative_cache_lookup_user_by_uid()`, `idmapper_negative_cache_lookup_user_by_name()`, and `idmapper_negative_cache_lookup_group_by_name()`.
- DBus methods expose negative users, groups, and UIDs when `USE_DBUS` is enabled.

## Control flow
Initialization creates three rwlocks, initializes three AVL trees with name or UID comparators, and initializes FIFO queues. Add-by-name allocates a struct plus inline name buffer, selects the proper tree, queue, capacity limit, metric entity, and label text, then AVL-inserts it. Duplicate inserts refresh the old entity timestamp and move it to the FIFO tail. New inserts are appended to the tail, and over-capacity caches evict the FIFO head.

Add-by-UID follows the same pattern using the UID tree. Lookups build a stack prototype and search the relevant AVL tree under the caller-held read lock. A present but expired entity returns false and records a miss; physical removal is deferred to the reaper. Reaping runs for users, groups, and UIDs, taking each write lock and removing expired FIFO heads until the first live entity.

## State and persistence
All state is in memory. Validity and capacity are controlled by `nfs_param.directory_services_param.negative_cache_time_validity`, `negative_cache_users_max_count`, and `negative_cache_groups_max_count`; the UID negative cache currently uses the user max-count parameter. Entry totals, reaped entries, evicted durations, and lookup hits/misses are reported to idmapper monitoring.

## Dependencies and integration points
The file depends on `avltree`, `TAILQ`, pthread rwlocks, `gsh_buffdesc_comparator()`, Ganesha allocation/logging, global directory-service configuration, DBus support, and `idmapper_monitoring`. It is used by higher-level idmapper resolution paths to short-circuit repeated not-found lookups and pairs with the positive cache in `idmapper_cache.c`.

## Risks
- Like the positive cache, expired negative entries can remain in AVL trees until reaped. Callers must use the boolean return, not mere tree presence.
- Add and lookup functions rely on caller-held locks as documented; the file itself does not acquire locks for public add/lookup paths.
- UID negative cache capacity uses the user negative-cache max count, which may be intended but should be validated when changing configuration semantics.
- DBus display takes a write lock while only iterating; this is conservative but can block add/reap operations longer than a read lock would.
- Metric calls for name-cache misses happen only after a tree hit or typed switch path; a missing name node returns false without recording a cache-use miss, unlike UID lookup.

## Test signals
- Tests should cover insert, duplicate refresh and FIFO tail movement, lookup hit, expired lookup miss, and reaper removal for all three entity types.
- Capacity tests should exceed user, group, and UID limits and verify oldest-entry eviction and cached-duration metrics.
- Lock-contract tests or thread sanitizers should exercise concurrent readers with serialized writers.
- DBus builds should validate string/epoch output for users, groups, and UIDs.
- Resolver integration tests should verify repeated failed lookups are suppressed until validity expires.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_negative_cache.c -->
