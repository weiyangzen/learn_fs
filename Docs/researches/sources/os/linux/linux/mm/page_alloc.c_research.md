# File Research: sources/os/linux/linux/mm/page_alloc.c

Linux zoned buddy page allocator. This file owns the core physical page allocation and free paths, per-CPU page caches, zone watermarks, NUMA zonelists, allocation slowpath policy, contiguous page allocation, memory hotplug interactions, and allocator-facing debugging/accounting hooks.

Key responsibilities:
- Maintains global allocator state: node states, zone names, migratetype names, `gfp_allowed_mask`, lowmem reserve ratios, watermarks, defrag mode, movable zone metadata, and NUMA node counts.
- Encodes and updates pageblock state, including migratetype, isolation bits, compaction skip bits, and sparse/flatmem pageblock bitmaps.
- Implements buddy free-list manipulation: add, move, delete, merge, split, expand, account free pages, and choose tail/head placement.
- Prepares pages for free and allocation, integrating page owner, page table checks, KASAN/KMSAN, debug pagealloc, init-on-free/init-on-alloc, memory allocation profiling tags, memcg kmem charging, page poisoning, and architecture hooks.
- Manages per-CPU page lists (`pcp`) for low-order pages and THP-sized PCP orders where enabled, including locking, batching, high/low tuning, draining, decay, CPU hotplug, and cache-slice-aware high-order free batching.
- Allocates from zones through fast paths and slow paths, including cpuset restrictions, dirty throttling placement, watermark checks, node reclaim, deferred struct page initialization, unaccepted memory acceptance, per-migratetype fallback, CMA fallback, and highatomic reserves.
- Implements reclaim/compaction/OOM retry policy for `__alloc_pages_slowpath()`.
- Exports public allocator APIs: `__alloc_pages_noprof()`, `__folio_alloc_noprof()`, `get_free_pages_noprof()`, `get_zeroed_page_noprof()`, `__free_pages()`, `free_pages()`, `alloc_pages_exact_noprof()`, `free_pages_exact()`, `alloc_pages_bulk_noprof()`, contiguous allocation helpers, and no-lock allocation helpers.
- Builds zonelists for UMA and NUMA, including fallback node ordering, memoryless-node local-memory mapping, and hotplug-safe rebuild sequencing.
- Computes and updates zone watermarks, lowmem reserves, total reserve pages, `min_free_kbytes`, per-zone PCP batch/high limits, and related `vm` sysctls.
- Supports memory hotremove/offline by disabling PCPs, draining isolated pages, removing isolated buddy pages, and reporting managed page counts.
- Supports optional unaccepted memory by lazily tracking unaccepted MAX_ORDER pages and accepting them on allocation pressure.
- Supports memory failure by taking poisoned pages off the buddy allocator and putting them back safely.

Important behavior:
- Freeing normal pages flows through `__free_pages_prepare()`, then either PCP lists or direct buddy insertion via `free_one_page()` / `__free_one_page()`.
- `__free_one_page()` merges buddies upward while respecting pageblock migratetype boundaries, isolate/CMA/highatomic accounting, compaction capture, guard pages, page reporting, and shuffled/tail placement.
- Allocation first tries PCP lists for eligible orders; failing that, it locks the zone and uses the buddy allocator through `rmqueue_buddy()`.
- Migratetype fallback is staged: preferred freelist, CMA fallback for movable allocations, whole-pageblock claiming to reduce fragmentation, and finally single-page stealing if allowed.
- Watermark checks subtract unusable free pages such as highatomic reserves and CMA pages unavailable to the allocation.
- High-priority and nonblocking allocations can dip into reserves; OOM victims and `__GFP_MEMALLOC` get special reserve handling.
- Slowpath allocation wakes kswapd, retries adjusted allocation flags, performs direct reclaim, performs direct compaction, handles cpuset/zonelist races, may invoke OOM, and treats `__GFP_NOFAIL` as a retrying special case.
- `alloc_pages_bulk_noprof()` is order-0 only, avoids memcg accounting and page-owner recursion, and uses PCP batching when a local allowed zone satisfies low watermarks.
- Exact-size allocation overallocates to a power-of-two order, splits the allocation, and frees unused tail pages.
- Contiguous allocation isolates pageblocks, migrates movable pages, grabs isolated free pages, optionally splits them to order-0, and undoes isolation afterward.
- PCP disabling sets per-zone PCP high limits to zero and forces all CPUs to drain; this is used for hotplug and page isolation-sensitive paths.
- `alloc_pages_nolock_noprof()` is a best-effort reentrant allocator for arbitrary contexts. It only tries PCP/trylock paths, avoids reclaim and kswapd wakeups, and is expected to fail easily.

Dependencies:
- Core MM: zones, nodes, zonelists, GFP flags, folios, page flags, pageblocks, compaction, reclaim, OOM, migration, memory hotplug, page isolation, hugetlb, CMA, memcg, KSM/THP watermarks, vmstat, and page reporting.
- Debug/accounting systems: KASAN, KMSAN, page owner, page table check, debug pagealloc, kernel page poisoning, lockdep, PSI, delay accounting, fault injection, allocation profiling tags, and tracepoints.
- Concurrency primitives: zone spinlocks, PCP spinlocks with CPU pinning/migration disabling, seqlocks for zonelist updates, mutexes for PCP draining and PCP batch/high updates, CPU hotplug callbacks, RCU-adjacent hotplug assumptions, and IRQ-safe locking.
- Architecture and platform hooks: memory acceptance, highmem clearing, arch page allocation/free hooks, NUMA distance, cacheinfo, and optional memoryless-node support.

Notable risks:
- Correctness depends on tight invariants around page refcounts, PageBuddy, page private order, pageblock migratetypes, zone accounting, PCP counts, and free-area lists.
- PCP locking is deliberately subtle: a PCP lookup must be paired with CPU pinning, and trylock failure can redirect pages to direct buddy free paths or per-zone lockless lists.
- Migratetype fallback and pageblock claiming trade locality, fragmentation, CMA usability, highatomic reserves, and future compaction success.
- Watermark and reserve checks are performance-sensitive and intentionally approximate in places; changes can alter allocation latency or premature reclaim behavior.
- Slowpath retry policy coordinates reclaim, compaction, OOM, cpuset races, zonelist rebuilds, and nofail semantics; small logic changes can cause livelocks or premature failures.
- Memory hotplug/offline and contiguous allocation depend on pageblock isolation and full PCP draining to prevent isolated pages from being reallocated.
- KASAN/page poisoning/init ordering is intentional: poisoning/unpoisoning and memory initialization must remain synchronized to avoid false reports or stale tags.
