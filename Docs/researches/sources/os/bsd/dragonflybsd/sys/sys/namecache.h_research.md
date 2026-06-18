# File Research: sources/os/bsd/dragonflybsd/sys/sys/namecache.h

DragonFlyBSD namecache and namecache-handle interface for filesystem namespace management.

Key responsibilities:
- Defines `struct namecache` for cached namespace entries, child/parent topology, vnode association, hash linkage, mount generation, generation tracking, references, timeout, flags, and lock.
- Defines `struct nchandle`, pairing a namecache pointer with a mount reference for overlay-aware path topology.
- Defines namecache flags for unresolved, whiteout, mount point, cache/no-cache chflags, symlink, directory, destroyed, deferred zap, world-searchable shortcut, and dummy nodes.
- Defines cache invalidation flags.
- Declares kernel APIs for locking, lookup, mount-point handling, invalidation, resolution, reference/copy/drop, rename/unlink, vnode conversion, full path construction, root setup, and per-CPU rollup.

Important behavior:
- DragonFly maintains namecache topology from active nodes to root except for NFS server and removed-file cases.
- Multiple namecache entries may pass through one vnode due to mount overlays, nullfs, union mounts, and mount crossings.
- Namespace locking must be performed on the cache record whose parent represents the physical directory for the operation.
- Generation changes are bracketed so unlocked accessors can detect concurrent changes and retry.

Dependencies:
- Includes `types.h`, `lock.h`, `queue.h`, and `spinlock.h`.
- Kernel APIs depend on vnodes, mounts, credentials, component/nlookup data, processes, and globaldata.

Notable risks:
- Namecache/vnode/mount topology is subtle; using the wrong `nchandle` across overlays can lock or operate on the wrong namespace.
- Generation and reference protocols must be followed to avoid stale unlocked lookups.
- Negative entries, whiteouts, destroyed entries, and unresolved entries have distinct semantics.
