# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_bio.c

Read completely: 5677 lines, 152944 bytes.

Implements FreeBSD's core buffer-cache and BIO support layer. It coordinates vnode buffers, VM object-backed buffers, buffer KVA, clean/dirty queueing, delayed writes, clustered async writes, buffer daemon flushing, BIO completion, pager reads through the buffer cache, and DDB diagnostics.

Major structures and global state:
- Defines `buf_ops_bio`, the default `buf_ops` implementation for `bufwrite`, `bufstrategy`, `bufsync`, and `bufbdflush`.
- Defines `struct bufqueue` and `struct bufdomain`; domains split clean/dirty/free accounting across up to `BUF_DOMAINS` domains.
- Maintains global static buffer headers in `buf`, addressed by `nbufp()`, while `buf_zone` provides UMA per-CPU caching over those fixed headers.
- Tracks clean queues, dirty queues, empty queues, buffer-space watermarks, dirty-buffer watermarks, KVA usage, malloc-backed small-buffer usage, and async running I/O pressure.
- Exposes many `vfs.*` sysctls for buffer space, dirty thresholds, free-buffer thresholds, running I/O thresholds, diagnostics counters, unmapped buffer control, and `maxbcachebuf`.

Initialization and sizing:
- `kern_vfs_bio_buffer_alloc()` sizes and reserves the static buffer-header array from estimated physical memory, `nbuf`, `maxbcache`, `maxbcachebuf`, and transient BIO mapping needs.
- `bufinit()` initializes locks, empty buffer headers, queues, buffer domains, `buffer_arena` reclaim hooks, UMA cache, watermarks, and counters.
- `maxbcachebuf_adjust()` clamps `maxbcachebuf` to a power of two bounded by `MAXBSIZE` and `maxphys`.
- Each `bufobj` is initialized by `bufobj_init()` with per-object clean/dirty pctries and queues and is assigned a buffer domain.

Buffer allocation and queueing:
- `getnewbuf()` reserves buffer space, obtains an empty header through `buf_alloc()`, allocates KVA with `getnewbuf_kva()`, recycles clean buffers if needed, and waits or helps flush when pressure persists.
- `buf_alloc()` pulls a header from `buf_zone`, initializes all buffer fields, assigns its domain, and locks it.
- `buf_free()` releases credentials, softdep dependencies, KVA, free-buffer accounting, and returns the header to UMA.
- `buf_recycle()` scans the clean queue, applies a second-chance `B_REUSE` policy, skips background-write buffers, invalidates a clean buffer, and releases it.
- `bremfree()` marks a locked queued buffer for delayed removal; `bremfreef()` immediately removes it.
- `binsfree()`, `bq_insert()`, `bq_remove()`, `bd_flush()`, and `bd_flushall()` manage movement among dirty, clean, per-CPU clean subqueues, and the empty queue.

Buffer-space and daemon behavior:
- `bufspace_reserve()`, `bufspace_adjust()`, and `bufspace_release()` account reserved/actual buffer memory and wake space daemons at thresholds.
- `bufspace_daemon()` runs per buffer domain to reclaim clean buffers and keep free headers and buffer space above low-water targets.
- `buf_daemon()` is the dirty-buffer flusher. It wakes from `bd_wakeup()`/`bd_speedup()`, walks domains, and calls `buf_flush()` until dirty counts fall below target.
- `flushbufqueues()` scans the dirty queue with a sentinel, skips locked or inappropriate buffers, handles invalid buffers, respects softdep dependencies unless forced, takes vnode/write locks with NOWAIT semantics, and writes buffers synchronously or asynchronously.
- `bwillwrite()` blocks writers before vnode locking when dirty-buffer counts are severe.

Read and write paths:
- `breadn_flags()` is the main `bread()`/`breadn()` path. It calls `getblkx()`, starts a read if `B_CACHE` is absent, optionally records checksum callbacks, sets credentials/accounting, and starts read-ahead through `breada()`.
- `breada()` asynchronously reads uncached read-ahead blocks.
- `bufwrite()` handles synchronous and asynchronous writes, cleans delayed-write state, sets `B_CACHE`, busy-marks VM pages, charges running I/O space, dispatches through strategy, and waits for sync callers.
- `bdwrite()` marks a buffer delayed-write, optionally triggers per-bufobj flush pressure, maps logical to physical block early, cleans VM page dirty bits into the buffer dirty range, and requeues it.
- `bdirty()` and `bundirty()` move buffers between clean/dirty bufobj lists and maintain per-domain dirty counters.
- `bawrite()`, `babarrierwrite()`, and `bbarrierwrite()` dispatch async/sync writes with optional write barriers.
- `bufbdflush()` limits per-bufobj dirty buildup by invoking `VOP_FSYNC()` or flushing a selected dirty buffer.

Lookup, creation, and resizing:
- `incore()` and `inmem()` test for cached buffer or fully valid VM-page residency.
- `getblk()` wraps `getblkx()`; `getblkx()` performs lockless then locked bufobj lookup, handles races, optional no-create/no-wait/sparse behavior, resizes existing buffers, commits unsafe delayed-write buffers, and creates new VMIO or non-VMIO buffers when absent.
- `geteblk()` returns an anonymous invalid buffer of a requested size.
- `allocbuf()` resizes buffer backing. Non-VMIO buffers use small malloc storage or anonymous wired pages; VMIO buffers attach pages from the vnode VM object and adjust `B_CACHE` based on page validity.
- `vfs_nonvmio_extend()`, `vfs_nonvmio_truncate()`, `vm_hold_load_pages()`, and `vm_hold_free_pages()` manage anonymous backing pages.
- `vfs_vmio_extend()`, `vfs_vmio_truncate()`, and `vfs_vmio_invalidate()` manage VM-object pages, KVA mappings, validity, dirty state, and release policy.

VMIO and page-cache integration:
- `vfs_busy_pages()` prepares VMIO pages for strategy I/O, increments paging-in-progress, shared-busies pages, records dirty ranges, write-protects pages for writes, and substitutes `bogus_page` for fully valid pages during partial-buffer reads.
- `vfs_vmio_iodone()` validates pages after reads, restores bogus pages, unbusies pages, and wakes object paging waiters.
- `vfs_unbusy_pages()` unwinds page busy state for incomplete I/O.
- `vfs_clean_pages_dirty_buf()` captures dirty ranges from VM pages and marks buffer pages valid/clean for delayed writes.
- `vfs_bio_set_valid()`, `vfs_bio_clrbuf()`, and `vfs_bio_bzero_buf()` expose buffer validation and zeroing helpers for mapped and unmapped buffers.
- `vmapbuf()` and `vunmapbuf()` map user pages into pager buffers or leave them unmapped when supported.

Clustered writes and BIO completion:
- `vfs_bio_clcheck()` checks adjacent delayed-write buffers for cluster eligibility.
- `vfs_bio_awrite()` builds clustered async writes for regular-file delayed-write buffers when contiguous logical and physical layout permits; otherwise it writes one buffer asynchronously.
- `biodone()` completes raw BIOs, handles panic-dump deferral, tears down transient mappings, and either wakes waiters or calls custom completion.
- `biowait()` waits for BIO completion and propagates normal or extended errors.
- `biofinish()` records an error/devstat completion and calls `biodone()`.
- `bufdone()` completes buffer I/O, wakes running-I/O waiters, invokes optional buffer callbacks, updates VMIO cache/page state, completes softdep state, runs checksum callbacks, and releases or wakes the buffer.
- `bufwait()`, `bdone()`, and `bwait()` provide buffer completion waits/wakeups.

Pager and device integration:
- `bdata2bio()` converts a `struct buf` into BIO data fields, using `bio_ma`/`BIO_UNMAPPED` for unmapped buffers.
- `memdesc_bio()` exposes BIO memory as a `memdesc` from vlist, VM pages, or virtual address.
- `bufstrategy()` dispatches non-device vnode buffers to `VOP_STRATEGY()`.
- `bufsync()` delegates to `VOP_FSYNC()`.
- `vfs_bio_getpages()` implements the buffer pager path for vnode page faults, aligning reads to filesystem block boundaries, downgrading and re-upgrading page busy state, using `bread_gb()`, supporting read-behind/read-ahead counts, and retrying if pages were invalidated during shared-busy windows.

Shutdown and diagnostics:
- `bufshutdown()` syncs filesystems, loops while busy or delayed-write buffers remain, reports stuck buffers when requested, swaps off, and unmounts filesystems when clean.
- DDB commands `show buffer`, `show bufqueues`, `show lockedbufs`, `show vnodebufs`, and `countfreebufs` inspect buffer state, domains, queues, locked buffers, vnode buffer lists, and free-buffer counts.

Key invariants and risks:
- Buffer flags are highly stateful. `B_CACHE`, `B_INVAL`, `B_DELWRI`, `B_RELBUF`, `B_NOCACHE`, `B_VMIO`, `B_ASYNC`, `B_REMFREE`, `B_MANAGED`, `B_DIRECT`, and background-write flags must remain consistent with queue membership and VM page state.
- Lock ordering is delicate: bufobj locks, buffer locks, vnode locks, queue locks, and daemon locks are intentionally combined with NOWAIT paths to avoid deadlocks.
- Dirty-buffer pressure and space-reclaim logic can deadlock if callers hold vnode or buffer locks while waiting in the wrong path.
- VMIO correctness depends on exact page valid/dirty/busy accounting and careful `bogus_page` restoration.
- Unmapped-buffer and transient-mapping support depends on `unmapped_buf`, `bio_ma`, KVA allocation, and `pmap_qenter/qremove` staying paired.
- Error handling intentionally re-dirties most failed writes except selected invalidation/device-gone cases; changing this can lose data or create unretryable dirty buffers.
- `getblkx()` races are explicitly handled by identity revalidation and retries; weakening those checks can return buffers for the wrong vnode/block.
