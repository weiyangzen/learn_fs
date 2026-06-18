# File Research: sources/os/bsd/openbsd-src/sys/sys/buf.h

Purpose: Defines the kernel buffer cache I/O structure, buffer queues, flags, cache accounting, and buffer-cache APIs.

Key contents:
- Buffer queue support includes FIFO and NSCAN queue types, high/low outstanding write limits, queue state fields, and enqueue/dequeue/drain/wait/done/quiesce/restart APIs.
- `struct buf` describes one kernel I/O buffer: tree/list links, process, flags, sizes, residual/error, device, data pointer, physical I/O save address, vnode association, UVM object/page state, logical/physical block numbers, completion callback, dirty/valid byte ranges, and queue linkage.
- Defines buffer cache queues and aggregate page counters for hot, warm, and cold queues.
- `B_*` flags cover async/sync behavior, busy/done/error state, delayed write, cache status, physical/raw I/O, invalidation, wanted wakeups, write in progress, deferred/scanned/page-daemon/released/warm/cold/cache-managed states.
- `clrbuf()` zeros buffer data and clears residual.
- Defines low-level allocation flags `B_CLRBUF` and `B_SYNC`.
- `struct cluster_info` tracks read-ahead and write-clustering state.
- Kernel declarations cover bread/breadn/bwrite/bawrite/bdwrite, biodone/biowait, brelse, getblk/geteblk/incore, dirty/undirty/reassign, vnode-buffer association, buffer memory mapping/page allocation, physio/minphys, buffer daemon, and clustered reads.

Filesystem relevance:
- This is a central block I/O and buffer-cache interface for local filesystems, block devices, and vnode strategies.
- VOP strategy and bwrite dispatch ultimately operate on `struct buf` instances defined here.
