# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_cluster.c

This file implements clustered buffer-cache I/O for DragonFly BSD: synchronous and asynchronous read clustering, read-ahead marking, write clustering, write-behind heuristics, and clustered I/O completion fanout back to component buffers.

The file replaces older vnode-local clustering state with `struct cluster_cache`, a 4-way set-associative cache over vnodes and 1 MB logical zones. It tracks recent write clustering fields such as `v_lastw`, `v_cstart`, `v_lasta`, and `v_clen`. The cache is intentionally heuristic because vnode recycling can make entries stale, but it must remain self-consistent enough not to cluster unrelated offsets.

Tunables:
- `vfs.write_behind`: disables, enables, or backs off write-behind.
- `vfs.write_behind_minfilesize`: avoids write-behind for smaller files by default.
- `vfs.max_readahead`: caps desired read-ahead bytes.

Read path:
- `cluster_readx` replaces `bread()` with synchronous requested-block I/O plus asynchronous read-ahead.
- `cluster_readcb` is the asynchronous callback-based version.
- Both compute read-ahead from `minreq`, `maxreq`, `max_readahead`, file size, and block size.
- `B_RAM` marks a read-ahead trigger buffer; when later hit from cache, the code launches the next read-ahead window.
- `VOP_BMAP` is used to determine physical contiguity and burst size. If mapping fails or returns `NOOFFSET`, the path falls back to single-buffer I/O.

Cluster read construction:
- `cluster_rbuild` combines physically contiguous, VMIO-backed buffers into a synthetic cluster pbuf.
- It avoids buffers already cached, locked, partially valid, dependency-blocked for reads, or not VMIO-backed.
- It maps collected pages into the pbuf with `pmap_qenter_noinval`.
- Fully valid pages are replaced with `bogus_page` and flagged with `B_HASBOGUS` to avoid unnecessary disk reads.
- The function preserves the original requested buffer as part of the cluster when possible and returns either the cluster buffer or the original buffer.

Completion path:
- `cluster_callback` handles completion for clustered reads and writes.
- It propagates errors to component buffers, panics on unexpected short cluster I/O, unmaps pbuf pages, releases the pbuf to vnode or mount pbuf pools, and calls `biodone` for each component.
- For writes, it calls `bundirty` on successful component completion.
- For direct I/O component buffers it restores `B_RELBUF` if needed.

Write path:
- `cluster_write` implements delayed clustered writes for normal filesystem writes.
- It detects logical and physical sequentiality using the cluster cache and `bio_offset`.
- It may call `VOP_REALLOCBLKS` to make delayed buffers physically contiguous.
- It delays, asynchronously writes, or write-behind flushes depending on sequentiality, async mount state, `seqcount`, memory pressure, EOF position, and tunables.
- `cluster_wbuild_wb` gates write-behind by mode and minimum file size.

Forced async write:
- `cluster_awrite` is the clustered equivalent of `bawrite`.
- It guarantees the passed buffer is eventually initiated for I/O even if `cluster_wbuild` cannot include it.

Cluster write construction:
- `cluster_wbuild` scans dirty delayed-write buffers from a starting logical offset and builds a pbuf for contiguous compatible buffers.
- It requires buffers to be dirty, not invalid, not locked, clusterable, and compatible in VMIO/commit flags.
- It checks physical contiguity through `bio_offset` and caps page count by `vmaxiosize`.
- It handles VM page busy/io state, starts soft dependencies when needed, maps pages into the pbuf, marks running buffer space, and submits through `vn_strategy`.

Reallocation support:
- `cluster_collectbufs` gathers current cluster buffers plus the newest buffer for `VOP_REALLOCBLKS`.
- It avoids blocking on unavailable buffers and removes gaps before returning the `cluster_save` list.

Utility helpers:
- `cluster_getcache` and `cluster_putcache` manage heuristic locked cluster-cache entries.
- `calc_rbuild_reqsize` determines per-request read cluster size from desired read-ahead and device maximum.
- `cluster_append` links component buffers to a cluster bio.
- `cluster_setram` and `cluster_clrram` synchronize `B_RAM` with the first VM page's `PG_RAM`.

Notable dependencies include the buffer cache, vnode pager/VM pages, `VOP_BMAP`, `VOP_REALLOCBLKS`, `vn_strategy`, pbuf allocation, mount/vnode pbuf counters, and low-level pmap page mapping.

Implementation risks for future changes:
- Cluster pbufs borrow component pages and must pair every `vm_page_io_start`, object pip increment, and pmap mapping with the expected completion cleanup.
- `B_RAM` placement controls read-ahead behavior and can cause degenerate I/O if set incorrectly.
- Write clustering is conservative around dependencies and locked pages; relaxing checks can deadlock or violate softdep ordering.
- Mixed block sizes, especially noted for HAMMER, are guarded by file-size and block-size boundary checks.
