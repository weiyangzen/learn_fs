# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_cache.c

This file implements DragonFly BSD's namecache core: pathname component caching, vnode association/disassociation, negative cache entries, mountpoint traversal caching, namecache invalidation, root namecache setup, `getcwd`, and full-path reconstruction.

The central model is `struct namecache` as a tree plus hash table entry. Lookups are keyed by `(parent ncp pointer, component name)` using `nchashtbl`. Entries may be unresolved, positive-resolved to a vnode, or negative-resolved with `nc_vp == NULL`. Reference accounting is fundamental: a natural reference, a hash/topology reference, and either vnode-namecache or negative-list association references are carefully balanced. The code relies on the invariant that a final `1 -> 0` transition only destroys an unresolved, unlinked entry.

Key structures and caches:
- `struct nchash_head`: per-bucket list plus spinlock for namecache hash entries.
- `struct pcpu_ncache`: per-CPU negative-entry list, deferred zap count, and batched cache statistics.
- `struct mntcache` / `mntcache_elm`: per-CPU cache for frequently held mount and namecache references, reducing atomic refcount traffic.
- `struct ncmount_cache`: global set-associative cache mapping `(current mount, ncp)` to a mounted filesystem crossing result.

Important exported namecache lifecycle operations include `cache_hold`, `cache_drop`, `cache_copy`, `cache_get`, `cache_put`, `cache_lock`, `cache_unlock`, `cache_lock_maybe_shared`, `cache_zero`, `cache_changemount`, and `cache_drop_and_cache`. These wrap namecache and mount references together in `struct nchandle`.

Locking rules are explicitly encoded and high-risk:
- Namecache locks are generally ordered child-to-parent.
- Parent and child must both be locked to link a child into a parent's `nc_list`.
- Hash bucket spinlocks protect hash membership, but many lookup paths use generation/update-counter style validation to reduce blocking.
- Shared namecache locks are allowed for resolved entries unless disabled via `debug.ncp_shared_lock_disable`; unresolved or reclaimed vnode cases fall back to exclusive locking.

Association functions:
- `_cache_setvp` resolves an ncp to a vnode or to a negative entry, attaching to `vp->v_namecache` or a per-CPU negative list.
- `_cache_setunresolved` removes vnode or negative-list association and restores unresolved state.
- `_cache_auto_unresolve_test` and `_cache_auto_unresolve` expire timed entries and stale negative entries when a mount's namecache generation changes.
- `cache_settimeout` supports NFS-style timeout invalidation.

Invalidation and cleanup:
- `cache_inval` and `_cache_inval_internal` recursively invalidate topology, with deep recursion handled by `MAX_RECURSION_DEPTH` and resume tracking.
- `cache_inval_vp`, `cache_inval_vp_nonblock`, and `cache_inval_vp_quick` invalidate vnode associations, including a quick nonblocking path intended to help vnode recycling make progress.
- `cache_unlink` marks an entry destroyed and attempts vnode deactivation where appropriate.
- `cache_zap` removes trivial unresolved entries from topology and frees them, optionally walking upward.
- `cache_hysteresis`, `_cache_cleanneg`, `_cache_cleanpos`, and `_cache_cleandefered` enforce negative and unresolved cache pressure limits.

Lookup and resolution:
- `cache_nlookup` is the main new API lookup path. It returns a referenced, locked `nchandle`, creating unresolved entries when needed, reusing destroyed entries where possible, and updating per-CPU stats.
- `cache_nlookup_maybe_shared` is a nonblocking shared-lock lookup for already-resolved entries.
- `cache_nlookup_nonblock` is a nonblocking path used by NFS readdirplus-like code.
- `cache_nlookup_nonlocked` is an optimized resolved-entry lookup that returns failure on unstable state.
- `cache_resolve` resolves an unresolved ncp via `VOP_NRESOLVE`, handling destroyed entries, missing parent vnodes, mount roots, vnode reclaim races, and `EAGAIN` retry.
- `cache_resolve_mp` resolves a mount root through `VFS_ROOT`.
- `cache_resolve_dvp` resolves and returns a referenced parent directory vnode.

Mountpoint support:
- `cache_findmount` uses the set-associative `ncmount_cache` to avoid frequent `mountlist_scan` calls when crossing mountpoints.
- `cache_ismounting` precaches new mountpoint mappings and invalidates stale ones.
- `cache_unmounting` clears cache entries related to a mount while holding per-CPU unmount interlocks.
- `cache_clrmountpt` clears `NCF_ISMOUNTPT` after verifying no mount still references the ncp.

NFS and disconnected vnode support:
- `cache_fromdvp` reconstructs namecache topology from a directory vnode, mainly for NFS server file-handle paths.
- `cache_fromdvp_try` and `cache_inefficient_scan` perform parent lookup and directory scans when ordinary topology is absent or paths are extremely deep.
- This is intentionally isolated because disconnected-namecache merging would complicate the core model.

Path reconstruction:
- `kern_getcwd` and syscall wrapper `sys___getcwd` build the current working directory path from `fd_ncdir` up to `fd_nrdir`, crossing mount roots through `mnt_ncmounton`.
- `cache_fullpath` and `vn_fullpath` reconstruct paths from arbitrary nchandles or vnodes, with optional mountpoint guessing.

Initialization and stats:
- `nchinit` allocates per-CPU namecache state, initializes `nchstats`, creates the hash table, and initializes mount cache locks.
- `cache_allocroot` creates root namecache handles.
- `vfs_cache_setroot` installs the system root vnode/namecache handle.
- `vfscache_rollup_cpu` rolls per-CPU counters into global sysctl-visible totals.

Notable dependencies include `sys/namecache.h`, `sys/nlookup.h`, vnode and mount internals, `VOP_NRESOLVE`, `VFS_ROOT`, mountlist scanning, per-CPU globaldata, lockmgr, spinlocks, vnode hold/ref APIs, and sysctl.

Implementation risks for future changes:
- Refcount transitions, vnode hold/drop balancing, and negative-list membership are tightly coupled.
- Many paths intentionally release and reacquire locks to avoid deadlocks; race rechecks are not optional.
- Mount cache entries store namecache pointers for comparison without full ncp references, so invalidation ordering matters.
- `NCF_DESTROYED`, `NCF_UNRESOLVED`, `NCF_DEFEREDZAP`, `NCF_ISMOUNTPT`, and generation updates drive correctness across lookup, invalidation, rename, and path reconstruction.
