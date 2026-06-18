# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_cache.c

Read completely: 472 lines.

Implements OpenBSD's pathname namecache. It caches positive and negative directory lookups, keeps per-directory red-black trees for fast component lookup, tracks reverse directory-name mappings for `getcwd()`, and purges entries on vnode/filesystem invalidation.

Cache structures:
- Positive entries are counted in `numcache` and linked on `nclruhead`.
- Negative entries are counted in `numneg` and linked on `nclruneghead`.
- Each directory vnode owns a `v_nc_tree` keyed by component name length and bytes.
- Directory target vnodes keep reverse entries on `v_cache_dst`, excluding `.` and `..`.
- `doingcache` globally enables/disables namecache use.
- `nch_pool` allocates `struct namecache` entries.

Lookup and insertion:
- `cache_lookup()` rejects disabled caching and names longer than `NAMECACHE_MAXLEN`, then searches the directory vnode tree.
- Positive hits validate `nc_vpid` against the target vnode generation before returning a locked/referenced vnode.
- Negative hits return `ENOENT` except for final-component `CREATE`, where the stale negative entry is removed.
- `.` and `..` hits handle vnode locking carefully: `..` unlocks the parent before locking the child/parent combination required by lookup flags.
- Hits update LRU position and statistics; bad/false hits purge the entry.
- `cache_enter()` recycles old positive or negative entries once `numcache >= initialvnodes`, allocates a new entry, inserts into the directory tree, and records positive, negative, and reverse links.

Reverse lookup and purge:
- `cache_revlookup()` scans `v_cache_dst` to find a parent/name for a directory vnode and can prepend that name into a caller's buffer for `getcwd()`.
- `nchinit()` initializes LRU queues and the namecache pool.
- `cache_purge()` removes all reverse and child entries for a vnode, then bumps `v_id` to invalidate stale capabilities.
- `cache_purgevfs()` removes all cache entries whose directory vnode belongs to a mount being unmounted.

Risks and notes:
- A file comment explicitly notes namecache access should be locked; this implementation relies on existing kernel/VFS serialization assumptions.
- Generation checks via `v_id` are central to avoiding stale vnode hits after recycle or purge.
- Reverse lookup does not `vget()` the parent; callers must validate and lock the returned vnode if they need stable semantics.
- Negative cache growth is capped separately, but positive-entry pressure drives general recycling.
- Parent/leaf lock behavior in `cache_lookup()` must match `VOP_LOOKUP()` and namei contracts exactly.
