# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_cluster.c

## Purpose
Implements clustered VFS buffer I/O for FreeBSD: synchronous reads with read-ahead, read cluster construction, delayed-write clustering, write-behind, and per-vnode cluster state initialization.

## Main Elements
- Initialization and tunables:
  - `cluster_init()` creates the secondary pbuf zone used for synthetic cluster buffers.
  - `vfs.write_behind` controls clustered write-behind behavior.
  - `vfs.read_max` and `vfs.read_min` bound read-ahead behavior.
- Read path:
  - `cluster_read()` replaces simple `bread` style access for filesystems that want clustered reads.
  - It fetches the requested logical block with `getblkx()`, honors cached hits, marks read-ahead positions with `B_RAM`, and detects sequential access using `seqcount`.
  - For non-cached sequential reads, it calls `VOP_BMAP()` to discover physical contiguity and builds larger I/O with `cluster_rbuild()`.
  - It issues the synchronous requested read first, then asynchronously schedules read-ahead buffers while respecting mount I/O size, file size, cache state, delayed writes, and sparse/unmapped flags.
- Read cluster construction:
  - `cluster_rbuild()` synthesizes a `B_CLUSTER` buffer over VM pages from multiple logical buffers.
  - It stops clustering on locked buffers, cached buffers, non-VMIO buffers, partially valid pages, invalid mappings, or mount I/O size limits.
  - It handles page busying, page-in-progress accounting, bogus-page replacement for already valid pages, optional unmapped buffers, and pmap temporary mappings.
- Cluster completion:
  - `cluster_callback()` propagates I/O errors from the synthetic cluster buffer to children, clears dirty/error state on success, restores `B_RELBUF` for direct I/O, completes child buffers, releases the pbuf vnode binding, and frees the pbuf.
- Write path:
  - `cluster_write()` tracks sequential write state in `struct vn_clusterw`.
  - It decides whether to start, extend, flush, delay, or bypass a cluster based on logical and physical contiguity, end-of-file position, async mount state, memory pressure, and `seqcount`.
  - It may call `VOP_REALLOCBLKS()` to make pending sequential logical writes physically contiguous.
  - It falls back to `bdwrite()` or `bawrite()` when clustering is not useful or possible.
- Write cluster construction:
  - `cluster_wbuild()` scans delayed-write buffers in logical order, locks only immediately available buffers, requires matching VMIO/cluster/write-credential characteristics, aggregates pages into a synthetic cluster buffer, transfers barriers, marks children async clean, and submits the cluster with `bawrite()`.
  - Returns the total byte count submitted.
- Helpers:
  - `cluster_wbuild_wb()` applies the `write_behind` policy.
  - `cluster_collectbufs()` reads and collects existing buffers plus the current buffer for block reallocation.
  - `cluster_init_vn()` resets per-vnode cluster-write tracking fields.

## Dependencies And Integration
Integrates with vnode buffer objects, `getblk`/`bread_gb`/`bdwrite`/`bawrite`, `VOP_BMAP()`, `VOP_REALLOCBLKS()`, VM page busying and object pip accounting, pbuf allocation, mount `mnt_iosize_max`, resource accounting, and process I/O statistics. Filesystems use these routines to improve sequential I/O throughput without implementing clustering internally.

## Risk Notes
Cluster construction is sensitive to buffer flags, page validity, VMIO state, physical block mappings, mount I/O limits, and lock availability. The code intentionally abandons clustering on many edge cases to preserve correctness. Non-page-aligned buffers require careful `b_data` offset inheritance, and the callback must correctly propagate errors to all child buffers. Write clustering can change behavior depending on memory pressure and the `write_behind` sysctl.
