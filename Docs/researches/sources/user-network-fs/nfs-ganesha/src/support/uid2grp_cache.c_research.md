# sources/user-network-fs/nfs-ganesha/src/support/uid2grp_cache.c

Purpose: owns the in-memory user-to-group cache used by `uid2grp.c`, indexed by both username and UID with FIFO expiration/eviction order.

Important APIs, types, and functions: `struct cache_info` links UID, uname, `group_data`, two AVL nodes, and FIFO queue entry. Public functions initialize/cleanup/reap the cache, add users, look up by name or UID, detect expiration, remove by name/UID, clear all entries, and optionally expose a DBus `show_uid2grp` method.

Control flow: `uid2grp_cache_init` initializes the rwlock, optional semaphore, AVL trees, hash shortcut array, and FIFO queue. `uid2grp_add_user` inserts into name and UID trees, replaces collisions, updates the direct UID cache slot, appends to FIFO, and evicts the oldest entry if capacity is exceeded. Reaping walks FIFO from oldest until the first non-expired item. Lookups use AVL for names and a UID hash shortcut plus AVL fallback for UIDs.

State and persistence: cache state is process-memory only: `uname_tree`, `uid_tree`, `uid_grplist_cache[1009]`, `groups_fifo_queue`, and `uid2grp_user_lock`. Each cached entry holds one reference on `group_data` and releases it on removal.

Dependencies and integration points: uses Ganesha AVL, BSD tail queues, atomics for read-lock UID shortcut access, `nfs_param` directory-service cache sizing, cleanup registration, monitoring counters, and optional DBus.

Risks: all public lookup/remove calls depend on callers holding the documented lock mode. `uid_grplist_cache[uid % id_cache_size] = NULL` clears the entire slot on removal, which is safe but may drop a shortcut to a different collided UID. The DBus method uses `snprintf(..., "%s", info->uname.addr)` even though `gsh_buffdesc` names are length-bearing and not guaranteed NUL-terminated for all sources. The `show_uid2grp` method allocates with `gsh_malloc` and frees with `free`.

Test signals: tests should verify replacement by uname and UID, capacity eviction, FIFO reap stop condition, hash shortcut fallback on collision, clear-cache reference release, and DBus rendering with non-NUL-terminated names.
