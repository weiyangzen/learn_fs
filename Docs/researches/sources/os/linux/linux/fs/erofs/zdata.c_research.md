# File Research: sources/os/linux/linux/fs/erofs/zdata.c

## Purpose
Implements compressed EROFS folio read and readahead, including pcluster sharing, compressed-page caching, bio submission, decompression scheduling, and decompressed-output distribution.

## Main Elements
- Core structures: `z_erofs_pcluster` represents a compressed physical cluster with lock/refcount, compressed bvecs, output bvecs, algorithm, size, and partial-decode state; `z_erofs_frontend` builds pcluster chains for a read; `z_erofs_backend` performs decompression.
- Bvec storage: inline bvecs plus linked bvset pages support variable numbers of output bvecs with `z_erofs_bvec_enqueue()` and dequeue helpers.
- Pcluster allocation: size-class slab caches are created by `z_erofs_create_pcluster_pool()` and used by `z_erofs_alloc_pcluster()`.
- Worker infrastructure: `z_erofs_init_subsystem()` initializes decompressors, pcluster slabs, and a high-priority workqueue; optional per-CPU kthread workers and CPU hotplug handlers provide lower-overhead atomic-context dispatch.
- Managed compressed cache: `z_erofs_init_super()` creates `managed_cache`, while `z_erofs_bind_cache()`, `z_erofs_cache_release_folio()`, `z_erofs_cache_invalidate_folio()`, and shrinker helpers connect cached compressed folios to pclusters.
- Pcluster registration and lifetime: `z_erofs_register_pcluster()`, `z_erofs_pcluster_begin()`, `z_erofs_get_pcluster()`, `z_erofs_put_pcluster()`, and `z_erofs_shrink_scan()` coordinate XArray lookup, deduplication of inflight work, lockref state, and RCU freeing.
- Frontend scan: `z_erofs_scan_folio()` maps logical ranges, handles fragments and holes, attaches folio pages to pclusters, tracks partial/full decode state, and marks online folio completion state.
- Backend decode: `z_erofs_decompress_pcluster()` builds input/output page arrays, handles overlapped in-place I/O, invokes the selected decompressor, copies secondary outputs, releases short-lived pages, and resets or frees pclusters.
- I/O submission: `z_erofs_fill_bio_vec()`, `z_erofs_submit_queue()`, and `z_erofs_endio()` prepare cached/in-place/temporary compressed pages, submit bios through block, file-backed, or fscache paths, and kick decompression after I/O completion.
- Address-space operations: `z_erofs_read_folio()` and `z_erofs_readahead()` implement compressed reads, readmore expansion, reverse-order readahead scanning, and queue execution.

## Dependencies And Integration
This file depends on EROFS mapping from `zmap.c`, decompressor backends, managed cache and shrinker utilities from `zutil.c`, block/fileio/fscache bio helpers, pagepool helpers, tracepoints, PSI memory-stall tracking, optional CPU hotplug and per-CPU kthreads, and VFS address-space operations.

## Risk Notes
Most risk is concurrency-related: pclusters are shared across reads through an XArray, protected by mutexes, lockrefs, spinlocks, and RCU. Managed folio `private` state, preallocated cache folios, in-place pages, short-lived pages, and bvec pages have different lifetimes and must not be mixed. Decompression can run synchronously, on an unbound workqueue, or on per-CPU kthreads, so bio completion and foreground waiting must preserve queue ownership. Partial decoding, fragments, metadata-backed compressed data, and file-backed/fscache I/O all add separate error and cleanup paths.
