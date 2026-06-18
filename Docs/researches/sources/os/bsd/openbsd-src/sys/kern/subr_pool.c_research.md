# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_pool.c

Implements OpenBSD’s kernel pool allocator: fixed-size object allocation from page-sized or larger backing chunks. It maintains per-pool empty/full/partial page lists, optional off-page page headers indexed by an RB tree, allocator backends, low/high/hard watermarks, deferred waiters, DDB diagnostics, sysctl export, stale-page garbage collection, and optional per-CPU caches on multiprocessor kernels.

Core state centers on `struct pool`, `struct pool_page_header`, `struct pool_item`, and the global `pool_head` list protected by `pool_lock`. `pool_init()` computes item alignment, page size, items per page, header placement, cache-coloring space, backing allocator choice, lock type, request queue state, and global serial registration. Large pools use multi-page allocators; small/aligned pools can store headers in-page, while off-page headers come from `phpool` and are tracked in `phtree`.

Allocation flows through `pool_get()` and `pool_do_get()`. `pool_get()` checks waitability, hard limits, optional per-CPU cache, then either obtains an item immediately or enqueues a `pool_request` and sleeps until `pool_get_done()` supplies memory. `pool_do_get()` reserves `pr_nout` before possibly dropping the pool lock to allocate a page, inserts a fresh page if needed, validates free-list magic, removes one item, moves pages between empty/partial/full queues, updates counters, and returns the object. `PR_ZERO` zeroes the item after allocation.

Freeing flows through `pool_put()` and `pool_do_put()`. `pool_put()` may hand the item to a per-CPU cache, otherwise returns it to its page, decrements outstanding counts, frees old idle empty pages above the high-water policy, and wakes queued requests. `pool_do_put()` locates the owning page via in-page header math or RB lookup, detects double free under diagnostics, restores free-list magic, poisons freed payloads when enabled, and moves pages between full/partial/empty queues.

Backing allocators are wrapped by `pool_allocator_alloc()`/`pool_allocator_free()`. Provided allocators include `pool_page_alloc()` for page-sized interrupt-safe allocations, `pool_multi_alloc()` for larger interrupt-safe allocations with `splvm()`, and `_ni` variants using `kv_any` and the kernel lock for non-interrupt-safe waitable allocation.

Reclamation includes explicit `pool_reclaim()`, global `pool_reclaim_all()`, and asynchronous GC through `pool_gc_tick`/`pool_gc_task`. GC scans all pools, optionally drains per-CPU cache lists, tries nonblocking pool locks, and frees stale empty pages older than `POOL_WAIT_GC`.

Under `MULTIPROCESSOR`, `pool_cache_init()` creates per-CPU fast caches backed by a separate `pool_caches` pool. `pool_cache_get()` and `pool_cache_put()` operate with `cpumem_enter()`, raised IPL, generation counters, list magic, poisoning checks, and per-CPU stats. Shared cache-list contention dynamically grows or shrinks `pr_cache_items`; sysctl helpers export aggregate and per-CPU cache metrics.

Diagnostics include `pool_chk_page()`, `pool_chk()`, `pool_walk()`, DDB pool printers, randomized free-list ordering, item magic tied to page magic, optional freed-item poisoning, and sysctl data via `sysctl_dopool()`. Lock abstraction supports either mutex-backed or rwlock-backed pools through `pool_lock_ops`; rwlock pools require `PR_WAITOK`.

Filesystem relevance: this is a foundational allocator used by kernel subsystems including VFS, vnode/namei-style pools, buffer-related structures, and many OpenBSD object caches. Its wait semantics, interrupt constraints, and page reclamation behavior directly influence filesystem allocation paths and memory pressure behavior.
