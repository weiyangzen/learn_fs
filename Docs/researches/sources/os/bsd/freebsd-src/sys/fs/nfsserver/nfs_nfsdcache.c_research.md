# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdcache.c

## Purpose

Implements the NFS server duplicate/recent request cache for NFSv2/v3 UDP and NFSv2/v3/v4 TCP request handling. Its job is to avoid redoing non-idempotent RPCs after client retries, while being deliberately conservative about false cache hits. NFSv4.1 is mostly outside this file’s active duplicate-reply path because `nfs_nfsdkrpc.c` routes v4.1 reply caching through session slots.

## Main Data and Tunables

The file uses `struct nfsrvcache` from `sys/fs/nfs/nfsrvcache.h`, which stores hash links, UDP LRU links, RPC xid, procedure, version flags, cached reply/status, UDP client address, TCP socket reference, request length, short checksum, TCP send sequence, ack state, timestamp, and seqid reference count.

Per-vnet cache tables:
- `nfsrvudphashtbl`: UDP hash table, protected by global `nfsrc_udpmtx`.
- `nfsrchash_table`: TCP duplicate cache hash table, with per-bucket mutexes.
- `nfsrcahash_table`: TCP ACK tracking hash table, with per-bucket mutexes.
- `nfsrvudplru`: UDP LRU/timeout queue.
- `nfsrc_tcpsavedreplies`, `nfsrc_udpcachesize`: saved-entry counters.

Sysctls/tunables:
- `vfs.nfsd.tcphighwater`: TCP saved-reply high-water mark; raising it can also raise `nfsrc_floodlevel`.
- `vfs.nfsd.udphighwater`: UDP cache high-water mark.
- `vfs.nfsd.tcpcachetimeo`: TCP cache timeout.
- `vfs.nfsd.cachetcp`: enables TCP caching for non-idempotent operations.
- `nfsrc_floodlevel`: per-vnet flood limit for TCP saved replies.

Static helpers include `newnfsv2_procid[]`, a generic-to-NFSv2 procedure mapping, and `nfsv2_repstat[]`, which identifies NFSv2 replies that can be cached as a status-only value instead of an mbuf chain.

## Entry Points

`nfsrvd_initcache()` allocates and initializes UDP, TCP, and ACK hash tables, initializes TCP bucket mutexes, list heads, the UDP LRU queue, and resets per-vnet counters.

`nfsrvd_getcache(struct nfsrv_descript *nd)` allocates a fresh `struct nfsrvcache`, fills in version/procedure/xid/socket metadata from the request descriptor, chooses UDP vs TCP from `nd_nam2`, and delegates to `nfsrc_getudp()` or `nfsrc_gettcp()`. It panics if asked to cache `NFSPROC_NULL`.

`nfsrvd_updatecache(struct nfsrv_descript *nd)` finalizes an in-progress cache entry after RPC execution. It clears `RC_INPROG`, handles the special `NFSERR_REPLYFROMCACHE` seqid case, and saves a reply when:
- the entry has an NFSv4 seqid reference count,
- UDP has `ND_SAVEREPLY`,
- TCP has `ND_SAVEREPLY`, TCP caching is enabled, and the flood level is not exceeded.

It stores either a status-only NFSv2 reply or an mbuf copy of `nd_mreq`. For TCP entries without seqid references, it returns the still-locked cache entry so `nfsrvd_sentcache()` can record the send sequence after the reply is actually sent.

`nfsrvd_delcache(struct nfsrvcache *rp)` invalidates an in-progress entry without sleeping and frees it if no reference or lock prevents that.

`nfsrvd_sentcache(struct nfsrvcache *rp, int have_seq, uint32_t seq)` records the TCP reply sequence number, inserts the entry into the ACK hash when applicable, marks it waiting for ACK, and unlocks the cache entry.

`nfsrvd_cleancache()` frees all TCP and UDP cache entries during server/module cleanup and resets counters.

`nfsrc_trimcache(uint64_t sockref, uint32_t snd_una, int final)` updates TCP ACK/NACK state for a socket, trims UDP entries by timeout/high-water pressure, and trims TCP entries by timeout, ACK, reference status, and high-water pressure. It uses a static `onethread` guard so only one trimmer runs at a time, and a histogram pass to choose a shorter temporary TCP timeout when the TCP cache is near high-water pressure.

`nfsrvd_refcache()` and `nfsrvd_derefcache()` maintain seqid-operation references from NFSv4 state owners. A `NULL` reference is accepted for NFSv4.1, where session slots replace this cache path.

## UDP Cache Behavior

`nfsrc_getudp()` keys entries by xid, RPC procedure, NFS version, and client IP address. On a hit:
- locked entries cause a sleep/retry loop,
- `RC_INPROG` means a duplicate request is dropped with `RC_DROPIT`,
- `RC_REPSTATUS` rebuilds a status-only reply,
- `RC_REPMBUF` copies the cached reply mbuf chain,
- successful completed hits refresh the UDP timeout and move the entry to the LRU tail.

On a miss, it increments cache miss/size counters, marks the new entry `RC_INPROG`, records IPv4 or IPv6 client address, inserts it into the UDP hash and LRU queue, assigns `nd->nd_rp`, and returns `RC_DOIT`.

## TCP Cache Behavior

`nfsrc_gettcp()` computes total request length and a checksum over the first `NFSRVCACHE_CHECKLEN` bytes, currently 100 bytes. It scans the TCP hash bucket for same xid, NFS version, procedure, length, checksum, and socket/timing constraints, temporarily removes candidate entries, and considers a hit only when exactly one candidate remains and no candidate has `rc_refcnt > 0`.

The TCP predicate is intentionally conservative. As written, completed-reply matching includes an `RC_NFSV4` requirement plus different socket reference and cache-time ordering; NFSv4.1 is bypassed earlier by `nfs_nfsdkrpc.c`. This means the durable TCP reply-hit logic is primarily for pre-v4.1 NFSv4. In-progress same-socket handling exists through `RC_SAMETCPCONN`, but completed TCP replay matching is constrained by the NFSv4 branch.

On a TCP hit:
- locked entries cause a sleep/retry loop,
- in-progress hits are dropped,
- status or mbuf replies are replayed,
- same-socket retry marking calls `nfsrc_marksametcpconn()`, which is currently a stub.

On a miss, it increments miss/size counters, stamps `rc_cachetime`, marks `RC_INPROG`, inserts the entry into the TCP hash table, assigns `nd->nd_rp`, and returns `RC_DOIT`.

## Locking and Lifetime

UDP entries use `nfsrc_udpmtx`. TCP entries use the hash-bucket mutex derived from xid. ACK hash operations use a separate ACK bucket mutex derived from socket reference.

`RC_LOCKED` and `RC_WANTED` implement per-entry exclusion and wait/wakeup. `nfsrc_freecache()` removes entries from their hash/LRU/ACK structures, wakes waiters, frees cached mbufs, decrements TCP saved-reply counters, frees the entry, and decrements global cache size.

Seqid-referenced entries are kept alive by `rc_refcnt`; they are freed only after dereference and once they are neither locked nor in progress.

## Integration Points

Called by `nfs_nfsdkrpc.c`:
- `nfsrvd_getcache()` before request execution,
- `nfsrvd_updatecache()` after request execution,
- `nfsrvd_sentcache()` after successful send,
- `nfsrc_trimcache()` during normal request handling and stream loss.

Used by NFSv4 state code:
- `nfsrvd_refcache()` and `nfsrvd_derefcache()` keep seqid-operation replies tied to open/lock owner state.

Initialized and cleaned by NFS server port/lifecycle code:
- `nfsrvd_initcache()` during server mount initialization,
- `nfsrvd_cleancache()` during server teardown.

## Risks and Review Notes

The cache prioritizes avoiding false hits over avoiding false misses. Request matching uses xid/procedure/version plus length and a short checksum, and TCP additionally uses socket reference/timing and seqid reference checks.

TCP saved replies are bounded by flood/high-water controls. When pressure is high, NFSv3 may skip saving replies and NFSv4 non-idempotent operations can surface resource-related behavior through callers.

`nfsrc_marksametcpconn()` is empty, so same-TCP-connection retry observation is not currently used beyond the immediate call sites.

The trim logic uses static globals such as `onethread`, `oneslot`, and last-trim timestamps; the cache tables are per-vnet, but these trimming throttles are process-global in this file.

Testing should focus on duplicate non-idempotent UDP operations, NFSv4 seqid replay behavior, TCP reply replay after reconnect, flood-level pressure, ACK-driven cleanup, and concurrent trim/update/free races.
