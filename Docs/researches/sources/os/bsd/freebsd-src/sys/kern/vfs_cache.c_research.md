# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_cache.c

## Purpose
Implements FreeBSD's VFS name cache and fast pathname lookup machinery. It caches individual path components, supports positive and negative lookup entries, resolves vnode-to-path strings for getcwd/realpath/auditing, provides cache maintenance hooks for VOP operations, and implements SMR/sequence-counter based lockless pathname lookup.

## Main Elements
- Cache data model:
  - `struct namecache` stores `(directory vnode, component name) -> vnode` mappings or negative entries.
  - `struct namecache_ts` extends entries with filesystem-supplied timestamps.
  - `struct negstate` and per-CPU-ish negative lists track negative cache hot/cold state and eviction.
  - Vnodes maintain source-entry lists, destination-entry lists, and `v_cache_dd` parent/dotdot shortcuts.
- Allocation and sizing:
  - Four UMA SMR zones hold small/large entries with or without timestamps.
  - `cache_symlink_alloc()` / `cache_symlink_free()` reuse namecache UMA zones for cached symlink bodies.
  - `nchinit()` initializes zones, hash table, bucket locks, vnode lock arrays, and negative-entry lists.
  - `cache_changesize()` rebuilds the hash table while preserving lockless lookup safety with temporary tables and SMR synchronization.
- Hashing and locking:
  - Hashes use FNV over the component name seeded by a per-vnode prehash.
  - Bucket locks protect hash chains; vnode-lock arrays protect vnode cache lists.
  - Insertion/removal code orders vnode locks and bucket locks carefully, including 3-vnode cases around directory parent entries.
- Lookup path:
  - `cache_lookup()` handles normal cache lookup using SMR when possible, with locked fallback.
  - Special cases support `"."`, `".."`, negative hits, whiteouts, CREATE-time negative invalidation, and timestamp returns.
  - `vfs_cache_lookup()` is the filesystem-facing VOP lookup wrapper that performs directory/read-only/execute checks, consults the cache, then calls `VOP_CACHEDLOOKUP()` on misses.
- Entry creation and invalidation:
  - `cache_enter_time()` inserts positive, negative, dotdot, and timestamped entries.
  - `cache_enter_time_flags()` supports `VFS_CACHE_DROPOLD`, mainly for filesystems such as NFS where target mappings may change.
  - `cache_remove_cnp()`, `cache_zap_locked()`, and helper paths remove entries by component.
  - `cache_purge()`, `cache_purge_vgone()`, `cache_purge_negative()`, and `cache_purgevfs()` remove entries for vnodes or entire mounts.
  - `cache_vop_rename()` and `cache_vop_rmdir()` keep cache state aligned with rename/rmdir operations.
- Negative-entry policy:
  - Negative entries are tracked separately from positive destination lists.
  - Hits increment a small hit counter and promote entries to hot lists after a threshold.
  - `cache_neg_evict()` demotes hot entries and evicts cold entries when total cache pressure or negative-entry ratios cross thresholds.
- Reverse path and syscall support:
  - `sys___getcwd()` and `vn_getcwd()` produce current working directory strings.
  - `sys___realpathat()` / internal realpath logic performs lookup then reconstructs canonical paths.
  - `vn_fullpath()`, `vn_fullpath_jail()`, and `vn_fullpath_global()` build paths relative to chroot, jail root, or global root.
  - `vn_fullpath_hardlink()` handles non-directory vnode path reconstruction using the parent/name captured by lookup.
  - `vn_vptocnp()` uses namecache reverse entries first, then falls back to `VOP_VPTOCNP()`.
  - `vn_path_to_global_path()` and hardlink variant rebuild a global path and re-lookup it to detect rename races.
- Lockless fast lookup:
  - `cache_fplookup()` is the fast path entered by `namei`.
  - `struct cache_fpl` tracks lookup state, saved fallback state, current/target vnodes, sequence counters, path position, and outcome.
  - `cache_can_fplookup()` rejects unsupported flags, Capsicum/cap-tracing, audit, explicit start directories, disabled fast lookup, and MAC cases.
  - `cache_fplookup_impl()` parses each component, runs filesystem `VOP_FPLOOKUP_VEXEC`, consults cache entries, crosses mount points, follows supported symlinks, and finalizes vnode refs/locks.
  - Partial fallback preserves progress by installing `ni_startdir` and compatible `nameidata` state for the regular locked lookup path.
  - `cache_symlink_resolve()` lets filesystem fast symlink handlers rewrite the remaining path buffer.
- Filesystem fast-lookup registration:
  - `cache_vop_vector_register()` ensures filesystems provide both fast lookup VOPs or neither.
  - `cache_validate_vop_vector()` asserts fast lookup mounts have valid `vop_fplookup_vexec` and `vop_fplookup_symlink`.
  - `cache_fast_lookup_enabled_recalc()` disables the fast path when sysctl or MAC policy makes it unsafe.
- Observability and diagnostics:
  - Numerous `vfs:namecache` and `vfs:fplookup` SDT probes expose lookup, insertion, purge, fullpath, and fast-lookup outcomes.
  - Sysctls expose cache size, hit percentage, positive/negative hit/miss counters, fullpath failures, negative eviction counters, and debug stats.
  - DDB `show vpath` prints cached reverse path chains.
- Inotify integration:
  - `cache_vop_inotify()` logs self and parent-directory events using cached destination entries and lazily clears `VIRF_INOTIFY_PARENT`.

## Dependencies And Integration
Uses FreeBSD VFS vnode/mount/namei interfaces, SMR, sequence counters, vnode ref/lock APIs, UMA, sysctl, DTrace SDT probes, Capsicum, MAC hooks, audit checks, inotify, KTRACE, DDB, and filesystem VOP methods. Filesystems integrate by routing lookup through `vfs_cache_lookup()`, inserting entries with `cache_enter*()`, purging via `cache_purge*()` or VOP cache hooks, and optionally implementing fast lookup VOPs under `MNTK_FPLOOKUP`.

## Risk Notes
This file is highly concurrency-sensitive. Correctness depends on SMR lifetime guarantees, sequence-counter validation, lock ordering across vnode and bucket locks, and careful fallback from lockless to locked lookup. Reverse path reconstruction is inherently best-effort for hardlinks and can race with rename. Negative-entry eviction is intentionally approximate and can fail under contention. The file also documents several known limitations: component rather than full-path caching, incomplete hardlink tracking, optional filesystem participation, wasted fixed-size entry space, duplicated tmpfs-style name storage, and performance bottlenecks around hashing and namei detours.
