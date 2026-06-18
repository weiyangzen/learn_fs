# File Research: sources/os/linux/linux-stable/fs/nfsd/nfscache.c

## Summary
Implements NFSD's duplicate reply cache, used to recognize retransmitted non-idempotent RPC calls and either replay a saved reply or drop duplicate in-progress requests. The cache is per NFSD network namespace, with hash buckets backed by red-black trees for lookup and per-bucket LRU lists for pruning.

## Main APIs
- Slab lifecycle: `nfsd_drc_slab_create()`, `nfsd_drc_slab_free()`.
- Per-net lifecycle: `nfsd_reply_cache_init()`, `nfsd_reply_cache_shutdown()`.
- Request path: `nfsd_cache_lookup()`, `nfsd_cache_update()`.
- Observability: `nfsd_reply_cache_stats_show()`.

## Data Model
Each bucket is `struct nfsd_drc_bucket`, containing an rb-tree, LRU list, and spinlock. Cache entries are `struct nfsd_cacherep` objects allocated from `drc_slab`; they carry a key made from XID, procedure, peer address/port, transport protocol, NFS version, argument length, and a weak checksum of the request payload.

Entries move through states such as unused, in-progress, and done. Reply types include no-cache, status-only replies, and short reply buffers. The implementation records whether the original request was secure so an insecure retransmission cannot read a cached secure reply.

## Behavior
`nfsd_reply_cache_init()` sizes the cache from available low memory, caps it at 256k entries, chooses a power-of-two bucket count targeting about eight entries per bucket, allocates the bucket table, and registers a shrinker named for the NFSD net namespace.

`nfsd_cache_lookup()` first skips work when the current thread-local cache type is `RC_NOCACHE`. Otherwise it computes a checksum over the leading RPC/NFS call bytes, preallocates a candidate entry, hashes by XID, and inserts or finds a matching rb-tree node under the bucket lock. On a miss it marks the entry `RC_INPROG`, prunes a few expired entries, updates miss and memory stats, and returns `RC_DOIT`. On a hit it drops the unused candidate, returns `RC_DROPIT` for in-progress duplicates, or appends/replays the cached status or buffer when safe.

`nfsd_cache_update()` finalizes an in-progress entry after dispatch. It refuses to cache missing status pointers, XDR failures, or replies larger than 256 bytes from the status pointer onward. Status-only replies store one status word; buffer replies allocate and copy the encoded status-plus-result segment. The entry is moved to the LRU tail and marked done.

The shrinker and shutdown paths prune entries through `nfsd_prune_bucket_locked()` and dispose them outside bucket lists. Pruning removes expired entries and also brings the cache back under its max-entry limit. Memory usage, hit/miss counters, not-cached counts, payload checksum misses, longest rb-chain length, and cache size at longest chain are exposed via `nfsd_reply_cache_stats_show()`.

## Dependencies
Uses Linux slab/vmalloc allocation, per-net NFSD state, rb-trees, lists, spinlocks, shrinkers, jiffies expiry, SunRPC request/reply buffers, socket address helpers, XDR buffer subsegments, page access, TCP-style checksum helpers, NFSD stats counters, and NFSD tracepoints.

Local headers are `nfsd.h`, `cache.h`, and `trace.h`.

## Risks
Cache-key correctness is essential. XID reuse is only safe because the key also includes address, port, protocol, version, procedure, argument length, and checksum. The checksum is deliberately weak, so payload mismatches are traced and counted but not suitable as a cryptographic guard.

The cache stores copied reply fragments rather than owning the original RPC send buffer. `nfsd_cache_update()` therefore depends on `statp` pointing into the encoded reply and on the 256-byte cap matching the intended DRC memory tradeoff.

Locking is per bucket. Entries must be unlinked from both rb-tree and LRU under the bucket lock, while freeing and buffer deallocation happen after unlinking. Shrinker and lookup pruning share the same invariants.

The current limit is per container/network namespace, so total memory can scale with the number of active NFSD namespaces despite the per-namespace cap.
