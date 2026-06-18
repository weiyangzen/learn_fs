# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_cache.c

## Purpose
Implements NetBSD's vnode name cache: per-directory name lookup, reverse lookup for `getcwd`/path reconstruction, negative entries, mountpoint entries, LRU replacement, cache invalidation, identity caching for fast access checks, and namecache statistics.

## Main Interfaces
- Lookup: `cache_lookup`, `cache_lookup_raw`, `cache_lookup_linked`, `cache_lookup_entry`.
- Reverse lookup: `cache_revlookup`.
- Insert/update: `cache_enter`, `cache_enter_id`, `cache_have_id`, `cache_enter_mount`, `cache_lookup_mount`, `cache_cross_mount`.
- Initialization: `nchinit`, `cache_cpu_init`, `cache_vnode_init`, `cache_vnode_fini`.
- Purge/invalidation: `cache_purge1`, `cache_purgevfs`, `cache_purge_parents`, `cache_purge_children`, `cache_purge_name`, `cache_remove`.
- Replacement: `cache_activate`, `cache_deactivate`, `cache_reclaim`.
- Statistics: `namecache_count_pass2`, `namecache_count_2passes`, `cache_update_stats`, `cache_stat_sysctl`.
- Debug: optional `namecache_print`.

## State And Control Flow
Each directory vnode owns an RB tree keyed by hash+name length for forward lookup. Each target vnode owns a list of parent/name entries for reverse lookup. Entries also live on global active/inactive LRU lists. Forward lookup holds the parent `vi_nc_lock`; reverse lookup holds child `vi_nc_listlock`; LRU reclaim uses `cache_lru_lock`. Positive entries point to a vnode, negative entries have `nc_vp == NULL`, and mountpoint entries use an empty synthetic name.

## Dependencies And Integration
Uses vnode implementation-private locks/lists, RB trees, pool cache allocation, kauth/genfs access checks, mount flags such as `IMNT_NCLOOKUP`, DTrace probes, per-CPU counters, callouts, sysctl, and vnode lifecycle hooks.

## Risks And Edge Cases
- The lock order is central: directory tree lock, vnode reverse-list lock, then LRU lock.
- Reverse purge intentionally handles child-to-parent lock inversion with try-locks, vnode holds, and retry pauses.
- `cache_lookup_linked` keeps namecache locks chained across path components and only works for filesystems that publish identity data.
- Negative entries are purged when creating the last path component.
- Reclaim is approximate by design and may temporarily exceed target size.
- `cache_revlookup` is not authoritative; on miss callers must fall back to directory scanning.

## Filesystem Relevance
Very high. This is the VFS path lookup acceleration layer used by namei, getcwd, mount crossing, vnode lifecycle, and filesystem lookup accounting.
