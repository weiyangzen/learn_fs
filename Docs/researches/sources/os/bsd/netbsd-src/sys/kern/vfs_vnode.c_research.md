# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_vnode.c

Read completely: 2178 lines.

## Purpose
Implements NetBSD vnode lifecycle and cache management: vnode allocation, reference/hold accounting, LRU draining, deferred release, cache lookup by filesystem key, rekeying, reclaim, revocation, dead-vnode transition, and vnode diagnostic helpers.

## Main Interfaces
- System setup: `vfs_vnode_sysinit`, `vcache_init`, `vfs_drainvnodes`.
- Marker and LRU helpers: `vnalloc_marker`, `vnfree_marker`, `vnis_marker`, `vrele_flush`.
- References: `vrefcnt`, `vput`, `vrele`, `vrele_async`, `vref`, `vhold`, `vholdl`, `holdrele`, `holdrelel`.
- Recycling/revocation: `vrecycle`, `vrevoke`, `vgone`, `vcache_make_anon`, `vdead_check`.
- Cache operations: `vcache_tryvget`, `vcache_vget`, `vcache_get`, `vcache_new`, `vcache_rekey_enter`, `vcache_rekey_exit`.
- Low-level reclaim/free: `vcache_reclaim`, `vcache_free`, `vcache_dealloc`.
- Misc helpers: `vwakeup`, `vnpanic`, `vshareilock`, `vshareklist`.

## State And Control Flow
The file documents and enforces a six-state vnode model: marker, loading, loaded, blocked, reclaiming, and reclaimed. State is normally protected by `v_interlock`; transitions out of loading also require `vcache_lock`. The high bits of `v_usecount` act as a gate for lockless `vcache_tryvget` and as a flag indicating a successful vget race.

`vcache_get` looks up a mount/key pair in a global hash. If present, it waits out loading and tries to reference the vnode. If absent, it allocates a loading vnode, inserts it, calls `VFS_LOADVNODE`, installs it on the mount, and transitions to loaded. `vcache_new` creates a filesystem node first and then inserts a keyed vnode, waiting for any old instance to be reclaimed.

Last-reference release runs through `vrelel`: it tries fast atomic release when not last, otherwise obtains or defers exclusive cleanup, clears mapping/text flags, calls `VOP_INACTIVE`, optionally blocks new references, and may reclaim. Reclaim purges namecache, invalidates buffers, revokes spec nodes, calls `VOP_RECLAIM`, removes the cache key, switches to dead vnode operations, and moves the vnode to `dead_rootmount`.

## Dependencies And Integration
Integrates with UVM vnode objects, name cache, mount busy/refcounting, fstrans, WAPBL, specfs, deadfs, threadpool jobs, sysctl hash statistics, kqueue vnode lists, readahead contexts, PAX segvguard cleanup, and vnode operation vectors.

## Risks And Edge Cases
- Last-reference handling is concurrency-heavy: `VUSECOUNT_GATE`, `VUSECOUNT_VGET`, interlock, vnode locks, and object locks must stay in sync.
- `vput` and `vrele` optimize for non-last references but fall back to `vrelel` when races occur.
- Deferred release avoids unsafe cleanup from pagedaemon or lock-failure contexts but requires the `LRU_VRELE` worker to make progress.
- Reclaim temporarily copies vnode keys so filesystem-owned key storage can vanish during `VOP_RECLAIM`.
- `vrevoke` suspends affected mounts while revoking device aliases and must handle cross-mount spec vnode aliases.
- `vcache_rekey_enter/exit` uses a placeholder loading vnode to prevent duplicate cache keys during filesystem key changes.

## Filesystem Relevance
High. This is the core vnode cache and lifecycle implementation that every NetBSD filesystem depends on for lookup identity, reference management, reclaim, revocation, and memory-pressure draining.
