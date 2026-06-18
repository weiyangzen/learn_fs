# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bio.c

## Purpose

`bio.c` implements illumos kernel buffer cache and page-I/O buffer support. It provides classic block-buffer operations used by UFS and block devices, delayed-write handling, buffer invalidation/flush paths, buffer header/memory recycling, and `buf(9S)` helper interfaces.

## Main Interfaces

Core block-buffer APIs include `bread`, `breada`, `bwrite`, `bwrite2`, `bdwrite`, `bawrite`, `brelse`, `getblk`, `getblk_common`, `trygetblk`, `bflush`, `blkflush`, `bfinval`, `binval`, `bio_busy`, `bcheck`, `iowait`, `iodone`, `biowait`, `biodone`, `geterror`, and `clrbuf`.

Page-I/O and driver helper APIs include `pageio_setup`, `pageio_done`, `bioerror`, `bioreset`, `biosize`, `biomodified`, `bioinit`, `biofini`, and `bioclone`.

Private machinery includes `bio_getfreeblk`, `bio_mem_get`, `bio_bhdr_alloc`, `bio_bhdr_free`, `bio_recycle`, `bio_flushlist`, `bio_incore`, `bio_pageio_done`, and `hash2ints`.

## Behavior And Data Flow

The buffer cache is organized by hash buckets in `hbuf`, delayed-write lists in `dwbuf`, and a free header list in `bhdrlist`. Each `buf` is protected primarily by `b_sem`, while hash/free-list structure is protected by bucket locks plus `blist_lock`, `bfree_lock`, and `bhdr_lock`.

`bread_common()` gets or allocates a buffer through `getblk_common()`, issues `bdev_strategy()` or UFS logging/snapshot strategy hooks if the buffer is not already `B_DONE`, waits with `biowait()`, and returns the locked buffer.

`bwrite_common()` sends the buffer through the block strategy or UFS logging/snapshot path, optionally waits, and optionally releases. `bdwrite()` marks a buffer as delayed write and complete, while `bawrite()` opportunistically sets `B_ASYNC`.

`brelse()` returns buffers to the correct free or delayed-write list. It handles failed retry writes, stale/error buffers, `B_NOCACHE` private buffers, and wakes memory waiters.

## Cache Management

`getblk_common()` searches the hash chain for a matching non-stale buffer, waits safely if the buffer is busy, handles identity changes after dropping locks, and allocates a new buffer if no match exists. If a duplicate appears while allocating, it frees the newly allocated memory/header and returns the existing buffer.

`bio_getfreeblk()` accounts against the buffer high-water memory budget, allocates a header, then allocates buffer memory. If memory allocation fails, it scans free lists for reusable buffers of the right size before falling back to sleeping allocation.

`bio_recycle()` reclaims aged free buffers, writes delayed-write buffers, frees memory and headers, and waits on `bio_mem_cv` if no reclaim path can satisfy the request.

`binit()` sizes the cache from `bufhwm`, `bufhwm_pct`, physical memory, and heap virtual memory, then initializes hash buckets, delayed-write buckets, and free-list accounting.

## Flush And Invalidate Semantics

`bflush()` serializes against invalidations, gathers delayed-write candidates without blocking under hash locks, then writes them asynchronously.

`blkflush()` targets one device/block delayed-write buffer and writes it synchronously in intent, though the file notes `B_ASYNC` can undermine that guarantee.

`bfinval()` invalidates all buffers for a device. With `force`, it can clear delayed writes and retry flags, move buffers from delayed-write to normal free lists, and mark them stale. Without `force`, delayed writes cause `EIO`.

## Page I/O

`pageio_setup()` allocates a `B_PAGEIO | B_NOCACHE` buffer over a page list, updates VM/page-in statistics, initializes semaphores, and holds the vnode.

`biodone()` routes async page I/O and remapped I/O to `bio_pageio_done()`. That path maps page completion to `pvn_read_done()` or `pvn_write_done()` and then destroys the pageio buffer through `pageio_done()`.

`biomodified()` tests whether pages in a pageio buffer have hardware modified state using `hat_pagesync()`.

## Notable Invariants

- `b_sem` is the exclusive buffer lock; `B_WANTED/B_BUSY` are not primary synchronization.
- Hash locks protect list membership and bucket lengths.
- `brelse()` expects a held `b_sem`.
- Buffers on delayed-write lists have `B_DELWRI`; non-delayed free-list scanning asserts otherwise.
- `B_NOCACHE` buffers are destroyed on release, not returned to the global cache.
- Pageio buffers hold vnode references until `pageio_done()`.

## Dependencies

This file depends on block device strategy dispatch, UFS logging/snapshot hooks, VM page/pvn APIs, HAT page attributes, kernel semaphores/condition variables, kstats, CPU stats, DTrace probes, and tunables in `var`.

## Research Notes

High-risk areas are lock ordering around hash lists versus `b_sem`, delayed-write flush/invalidation races, retry-write preservation, panic-time behavior in `getblk_common()`, buffer recycling under memory pressure, and pageio/remapped buffer cleanup.
