# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_rnode.c

Purpose: Manages NFSv4 client rnodes/vnodes, including hash lookup, freelist reuse, reclamation, attribute setup, open-list snapshots, and trigger stub state.

Key behavior:
- Initializes a global rnode hash table and `rnode4_cache`; each hash bucket has a reader/writer lock.
- Creates or finds vnodes by filehandle through `makenfs4node` and `makenfs4node_by_fh`, activating shadow vnodes when parent/name information is available.
- `make_rnode4` reuses freelist rnodes when possible, otherwise allocates vnode/rnode pairs, initializes locks, open-stream lists, delegation state, readdir cache, shared filehandle refs, vnode ops, and hash links.
- Maintains a freelist whose entries keep a vnode reference count of at least one to avoid VM races.
- `rp4_addfree` decides whether to cache, recycle, or destroy an rnode based on reference counts, dirty pages, delegations, open streams, recovery errors, unmount state, and allocation pressure.
- Provides hash insertion/removal, rnode lookup by filehandle, active-rnode checks, per-VFS destruction, global/per-VFS flushing, and attribute invalidation.
- Reclaim paths free access/readdir/symlink/ACL/xattr caches from free and active rnodes, then reclaim whole rnodes from the freelist if needed.
- `r4mkopenlist` snapshots valid open streams for recovery and discards/requires recovery for delegations.
- Provides helpers for clientid lookup, lease-time lookup, fsid-based rnode search, open-list release, and root-filehandle validation.
- Sets rnodes as mirror-mount or referral trigger stubs by switching vnode ops to trigger vnode ops.

Dependencies:
- Uses vnode/VFS/page APIs, DNLC, VM page lists, NFSv4 attr/cache/access/readdir/delegation/open/lock helpers, shared filehandles, shadow vnode support, recovery structures, and kmem reclaim callbacks.

Notable details:
- The documented lock order is hash bucket lock, then vnode lock, then freelist lock/rnode state lock as applicable.
- Hashing is by shared filehandle object address, not filehandle bytes.
- Misbehaving servers returning a different root filehandle for `"."` are corrected to the mount root filehandle.
- Rnodes with recovery failure are ignored by lookup and often destroyed instead of cached.
