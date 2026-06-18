# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_sfbuf.c

## Purpose

`subr_sfbuf.c` implements the machine-independent pool manager for `sf_buf` objects, used to create temporary kernel virtual mappings of VM pages for `sendfile(2)` and similar paths on platforms without a direct map.

If `PMAP_HAS_DMAP` is true, the file mostly bypasses pool management and treats a `vm_page *` as the `sf_buf` handle.

## Main Data Structures

Global state includes:

- `nsfbufs`: configured maximum number of buffers.
- `nsfbufsused`, `nsfbufspeak`: live and peak usage counters.
- `sf_buf_active`: hash table of active page-to-buffer mappings.
- `sf_buf_hashmask`: hash mask.
- `sf_buf_freelist`: tail queue of free buffers.
- `sf_buf_alloc_want`: number of waiters.
- `sf_buf_lock`: mutex protecting hash table, free list, counters, and refs.

The active hash key is derived from the page’s index in `vm_page_array`.

## Initialization

`sf_buf_init()` runs at `SI_SUB_MBUF`. If there is no direct map, it:

- Reads `kern.ipc.nsfbufs` tunable, defaulting to `512 + maxusers * 16`.
- Allocates the active hash table.
- Allocates a contiguous KVA region of `nsfbufs * PAGE_SIZE`.
- Allocates an array of `struct sf_buf`.
- Assigns each buffer one page of KVA and places it on the freelist.
- Initializes `sf_buf_lock`.

Sysctls under `kern.ipc` expose configured, peak, and current buffer counts.

## Allocation

`sf_buf_alloc(m, flags)` returns a buffer mapping for page `m`.

On direct-map systems it returns `(struct sf_buf *)m`.

Otherwise it:

- Requires CPU-private allocations to be made by pinned threads.
- Looks for an existing active mapping for `m`.
- If found, increments its refcount and removes it from the freelist if it was cached with refcount zero.
- If not found, takes the first freelist entry, sleeping unless `SFB_NOWAIT` is set.
- Recycles any old hash entry attached to that buffer.
- Inserts the buffer into the hash list, sets refcount/page, updates counters, and calls machine-dependent `sf_buf_map()`.

`SFB_CATCH` controls whether the sleep is interruptible. SMP/SFBUF_CPUSET builds may call `sf_buf_shootdown()` when reusing existing mappings.

## Freeing And Referencing

`sf_buf_free(sf)` decrements the refcount. When it reaches zero, the buffer is returned to the freelist and usage is decremented. If `sf_buf_unmap()` says the mapping was removed, the page association is cleared and the hash entry removed. Waiters are woken when present.

`sf_buf_ref(sf)` increments the refcount and asserts the buffer is allocated.

When `SFBUF_PROCESS_PAGE` is enabled, `sf_buf_process_page(m, cb)` finds the active buffer for page `m` and invokes a callback while holding `sf_buf_lock`.

## Dependencies

The implementation depends on VM page structures, pmap/KVA mapping helpers supplied elsewhere, mutexes, sleep/wakeup, sysctls, and optional SMP shootdown support.

## Maintenance Notes

The design intentionally keeps recently freed buffers mapped until recycling or explicit unmap, which can reduce mapping churn. The active hash and freelist are both protected by a single mutex, simplifying correctness.

Any change to refcount-zero cached mappings must preserve the distinction between “free but still associated with a page” and “unmapped/no page.” That distinction is visible in allocation reuse and `sf_buf_process_page()`.
