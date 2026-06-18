# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_bio.c

## Purpose

`vfs_bio.c` implements Darwin/XNU's BSD buffer I/O layer: `buf_t` state accessors, block read/write helpers, buffer-cache lookup and recycling, metadata buffer allocation, asynchronous I/O completion, delayed-write laundering, UBC-backed regular-file buffers, and temporary I/O buffers used by lower storage paths. It is the bridge between vnode-level filesystem operations, VM/UBC pages, and device `VNOP_STRATEGY` calls.

## Main Responsibilities

- Exposes the public kernel `buf_*` API for flags, sizes, credentials, device/vnode fields, UPL mapping, callbacks, verification metadata, and content-protection attributes.
- Maintains hashed cached buffers by `(vnode, logical block)` through `bufhashtbl`, with invalid buffers stored on `invalhash`.
- Maintains global free/reuse queues: `BQ_LOCKED`, `BQ_LRU`, `BQ_AGE`, `BQ_EMPTY`, `BQ_META`, and `BQ_LAUNDRY`.
- Provides synchronous, asynchronous, delayed, metadata, and read-ahead I/O paths through `buf_bread`, `buf_meta_bread`, `buf_breadn`, `buf_bwrite`, `buf_bdwrite`, and `buf_bawrite`.
- Integrates regular-file data buffers with UBC UPLs, while metadata buffers use kernel heap or kernel-map wired storage.
- Handles delayed-write pressure using `nbdwrite`, vnode write throttling, and a dedicated `bcleanbuf_thread`.
- Implements buffer invalidation and flushing by vnode through safe list iteration helpers.
- Provides shadow buffers for metadata I/O and callback/filter ownership patterns.
- Registers VM pressure cleanup via `vm_set_buffer_cleanup_callout(buffer_cache_gc)` and supports filesystem GC callouts.

## Key Data Structures And State

- `struct buf` headers are initialized in `bufinit()` from `buf_headers`; more can be allocated from `buf_hdr_zone` up to `max_nbuf_headers`, with temporary overcommit support.
- `bufhashtbl` stores valid cacheable buffers by vnode/block; `invalhash` stores invalid or empty buffers.
- `bufqueues[]` are tail queues used as buffer reuse lists. Timestamp thresholds (`lru_is_stale`, `age_is_stale`, `meta_is_stale`) drive `getnewbuf()` queue choice.
- `iobufqueue` stores reserved I/O-only headers for clone, cluster, shadow, and lower-level operations.
- `delaybufqueue` is declared, while delayed-write laundering actually uses `BQ_LAUNDRY`.
- `bufstats`, `nbdwrite`, `blaundrycnt`, `buf_busycount`, `needbuffer`, and `need_iobuffer` track pressure and waiters.
- `fs_callouts[]` stores up to 16 buffer-cache GC callbacks.

## Important Control Flow

- `bufinit()` initializes queues, hash tables, buffer headers, cluster support, the laundry thread, and VM pressure callback registration.
- `buf_getblk()` is the central cache acquisition path. It first probes the hash, waits on busy buffers when allowed, maps UBC pages for regular-file data, allocates metadata storage for metadata buffers, or obtains a recycled/new header via `getnewbuf()`.
- `getnewbuf()` prefers empty buffers, can grow header count, then chooses stale AGE/LRU/META buffers. Dirty reusable buffers are moved to `BQ_LAUNDRY` instead of being reused immediately.
- `bcleanbuf()` removes a buffer from its free queue, handles delayed-write laundering, detaches vnode/hash state, releases credentials and metadata storage, and returns a busy clean header ready for reuse.
- `bio_doread()` and `do_breadn_for_type()` implement `bread`/read-ahead on top of `buf_getblk()` and `VNOP_STRATEGY`.
- `buf_strategy()` maps logical file offsets to physical blocks with `VNOP_BLOCKMAP`, handles sparse/fragmented blocks, dispatches cluster buffers, sets content-protection offsets, and finally calls the device vnode strategy operation.
- `buf_bwrite()` clears delayed-write state, charges process/vnode output, issues `VNOP_STRATEGY`, and waits/releases for synchronous writes.
- `bdwrite_internal()` marks a buffer delayed and may force async writeback when delayed writes exceed 75% of buffer headers.
- `buf_brelse()` is the main release path: it commits or aborts UPLs, frees verification data, invalidates nocache/error buffers, moves buffers to an appropriate queue, handles shadow-master waits, clears busy state, and wakes waiters.
- `buf_biodone()` finalizes I/O, updates mount pending I/O counters, traces disk I/O, clears throttle/passive metadata, invokes callbacks or filters, releases async buffers, or wakes synchronous waiters.
- `buffer_cache_gc()` evicts stale metadata buffers in bounded batches, sending dirty ones to laundry and freeing clean metadata storage.

## Concurrency And Locking

- `buf_mtx` protects buffer hash membership, vnode clean/dirty lists, free queues, busy counts, and most buffer-cache state transitions.
- `iobuffer_mtxp` protects `iobufqueue`, I/O buffer usage counters, and virtual-device I/O buffer throttling.
- `buf_gc_callout` protects registration and dispatch of filesystem buffer-cache GC callbacks.
- Busy buffers use `BL_BUSY` plus `BL_WANTED` wait/wakeup discipline. Public wait paths commonly set wait bits under `buf_mtx`, sleep on the buffer, and retry.
- Vnode buffer iteration uses `VBI_ITER` and a temporary local list to avoid corrupting vnode clean/dirty lists while callbacks may drop locks.
- Shadow buffers require careful handling: parent buffers can stay off free lists while `b_shadow_ref` is nonzero, and `BL_WAITSHADOW`/`BL_WANTED_REF` coordinate waiters.
- The laundry thread avoids recursive stack/deadlock patterns by moving delayed write cleaning out of `getnewbuf()` callers.

## Edge Cases And Invariants

- Buffer hash list links use a `0xdeadbeef` sentinel through `BLISTNONE()` and diagnostic checks to catch double insertion/removal.
- `buf_getblk()` rechecks `incore_locked()` after `getnewbuf()` because allocating/recycling can drop `buf_mtx`.
- Metadata buffers smaller than `MAXMETA` are allocated from `KHEAP_VFS_BIO`; larger metadata buffers use `kmem_alloc`.
- Regular-file data buffers are usually UBC-backed; several development/debug checks panic if Apple filesystems call old `buf_getblk()` paths unexpectedly.
- Sparse block reads with physical block `-1` are zero-filled and completed without device I/O.
- `buf_strategy_fragmented()` splits logically contiguous but physically fragmented I/O into per-extent synchronous strategy calls.
- `buf_brelse()` treats metadata `B_FILTER` callbacks specially so HFS journaling filters are cleaned up even on invalidation.
- `alloc_io_buf()` reserves `NRESERVEDIOBUFS` for privileged callers and throttles disk-image/virtual-device mounts separately.
- Verification buffers are sized by block count and hash kind; cluster verification data is retrieved from UPL verification storage.
- Content-protection fields are compiled under `CONFIG_PROTECT`; non-protection builds provide no-op/NULL implementations.

## Filesystem Relevance

This file is central for understanding Darwin's historical BSD buffer cache as it coexists with UBC. Filesystem metadata still uses `buf_t` as a cache and I/O object, while regular-file data paths are VM-page backed. The file also shows how vnode-level operations are turned into block-device strategy calls, how dirty metadata is throttled and laundered, and how the kernel avoids deadlocks under memory and virtual-device pressure.
