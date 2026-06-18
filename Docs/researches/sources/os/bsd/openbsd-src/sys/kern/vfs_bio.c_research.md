# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_bio.c

Read completely: 1529 lines.

Implements OpenBSD's buffer cache core: buffer allocation, cached block lookup, read/write helpers, delayed-write handling, I/O completion, memory pressure backoff, cleaner daemon coordination, and the clean/dirty cache queues.

Core buffer-cache sizing and lifecycle:
- `bufinit()` sizes the cache from physical/free pages and `bufcachepercent`, enforces minimums, reserves buffer KVA, initializes `bufpool`, initializes cache queues, and sets dirty-page watermarks.
- `bufadjust()` changes `bufpages`, recomputes `targetpages`, recovers pages if over target, rebalances cache queues, and wakes the cleaner under pressure.
- `bufbackoff()` lets UVM force the buffer cache down toward `buflowpages`.
- `buf_put()` removes a buffer from the global list, frees attached memory through `buf_dealloc_mem()`, and returns it to `bufpool` unless KVA cleanup is deferred.

Read/write paths:
- `bio_doread()` wraps `getblk()`, starts `VOP_STRATEGY()` reads for uncached data, charges resource counters, and updates per-mount sync/async read stats.
- `bread()` performs synchronous block reads; `breadn()` adds independent async read-ahead.
- `bread_cluster()` issues one large read-ahead I/O when `VOP_BMAP()` reports contiguous blocks, then splits pages back into per-block buffers in `bread_cluster_callback()`.
- `bwrite()` handles sync and async writes, converts eligible sync writes to delayed writes on `MNT_ASYNC`, updates mount stats and output counters, starts strategy I/O, and waits/releases for synchronous callers.
- `bdwrite()` marks delayed-write buffers dirty and complete without immediate I/O.
- `bawrite()` marks a buffer async and dispatches through `VOP_BWRITE()`.

Buffer lookup and allocation:
- Buffers are indexed per vnode in `v_bufs_tree` by logical block number.
- `incore()` checks for a valid cached block.
- `getblk()` waits for busy matching buffers, returns cached buffers with `B_CACHE`, or calls `buf_get()` to allocate a new busy buffer.
- `buf_get()` allocates a `struct buf`, optionally associates it with a vnode, allocates/map pages for nonzero sizes, enforces cache and KVA reserve limits, and waits on `needbuffer`/`nobuffers` when non-cleaner callers hit pressure.
- `geteblk()` obtains an anonymous invalid buffer.

Release, dirtying, and completion:
- `brelse()` invalidates noncacheable/error buffers, frees invalid buffers immediately, otherwise returns valid buffers to the clean or dirty cache, clears transient flags, wakes waiters, and triggers reclamation/rebalancing.
- `buf_dirty()` and `buf_undirty()` toggle `B_DELWRI` under `splbio()` and call `reassignbuf()`.
- `biowait()` sleeps for `B_DONE` and returns `EINTR`, buffer error, `EIO`, or success.
- `biodone()` marks completion, updates queue and pending-I/O stats, wakes vnode output waiters, invokes callbacks, releases async buffers, or wakes sync waiters.
- `buf_adjcnt()` adjusts `b_bcount` within allocated buffer size.

Cleaner and cache policy:
- `buf_daemon()` sleeps on `bd_req`, drains dirty buffers from `dirtyqueue`, and writes them asynchronously until dirty/KVA pressure drops.
- The clean cache is a 2Q-style design with hot, cold, and warm queues.
- `bufcache_release()` places clean buffers in hot/warm queues and dirty buffers in `dirtyqueue`.
- `bufcache_take()` removes a buffer from its current clean or dirty queue and updates page counters.
- `chillbufs()` moves over-limit hot/warm buffers to cold.
- `bufcache_recover_pages()` discards clean buffers until enough pages are recovered.
- Hibernation support drops all clean cache pages instead of preserving them in swap.

Risks and notes:
- Correctness depends on strict `splbio()` discipline around buffer queues, vnode buffer lists, and cache counters.
- Buffer flags are stateful and overlapping; mistakes with `B_BUSY`, `B_DELWRI`, `B_INVAL`, `B_DONE`, `B_ASYNC`, or `B_WRITEINPROG` can corrupt lifetime or I/O accounting.
- `bread_cluster_callback()` moves pages between UVM objects after interrupt-time completion, making object/page offset invariants critical.
- Cleaner and syncer paths are exempt from some buffer pressure waits; changing reserve logic can deadlock memory reclaim.
- Write errors on regular-file buffers mark the vnode with `VBIOERROR`, so callers may observe damage after buffer release.
