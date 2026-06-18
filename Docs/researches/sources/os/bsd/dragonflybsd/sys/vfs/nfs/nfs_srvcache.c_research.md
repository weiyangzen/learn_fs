# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_srvcache.c

This file implements the NFS server duplicate request cache, based on the classic Chet Juszczak NFS server correctness/performance design. It is compiled only when server support is enabled.

Primary responsibilities:
- Size and initialize the duplicate request cache.
- Detect duplicate RPC requests by XID, procedure, and client address.
- Drop in-progress duplicates.
- Replay cached replies for completed non-idempotent operations.
- Reuse cache entries with LRU eviction.

Key data:
- `nfsrvhashtbl` hashes cache entries by XID.
- `nfsrvlruhead` tracks entries for eviction.
- `numnfsrvcache` and `desirednfsrvcache` control cache size.
- `srvcache_token` serializes cache access.
- `nonidempotent[]` marks operations whose replies must be cached.
- `nfsv2_repstat[]` marks NFSv2 operations where only status needs to be cached.

Key functions:
- `nfsrvcache_size_change()` chooses cache size as half `nmbclusters`, clamped to min/max bounds.
- `nfsrv_initcache()` allocates the hash table and initializes LRU state.
- `nfsrv_destroycache()` destroys the hash table after the LRU is empty.
- `nfsrv_getcache()` checks for an existing request and returns `RC_DOIT`, `RC_DROPIT`, or `RC_REPLY`; it inserts new misses as `RC_INPROG`.
- `nfsrv_updatecache()` marks a request done and stores status or a copied reply mbuf for non-idempotent operations.
- `nfsrv_cleancache()` frees all cache entries, cached replies, and stored socket addresses.

Important behavior:
- Reliable transports with no source address (`nd_nam2 == NULL`) bypass the duplicate cache.
- In-progress duplicates are dropped to avoid re-executing mutating operations.
- Completed non-idempotent duplicates receive cached replies when possible.
- Idempotent completed duplicates can be re-executed by resetting state to `RC_INPROG`.

Caveats:
- Cache entry locking is internal via `RC_LOCKED` and `RC_WANTED`; callers must not assume wait-free behavior.
- If the cache is too small, the same request can complete more than once after eviction/reuse, which is explicitly noted in `nfsrv_updatecache()`.
