# File Research: sources/os/linux/linux/mm/ksm.c

Linux Kernel Samepage Merging implementation. This file owns the `ksmd` scanner, KSM reverse-map metadata, stable and unstable content trees, KSM page replacement, KSM page reverse mapping, KSM sysfs controls, process/VMA enablement hooks, and memory hotplug/migration integration.

Key responsibilities:
- Defines KSM metadata structures: `ksm_mm_slot`, `ksm_scan`, `ksm_stable_node`, and `ksm_rmap_item`.
- Maintains stable and unstable RB trees, optionally per NUMA node when `merge_across_nodes` is disabled.
- Tracks global KSM accounting: scanned pages, shared nodes, sharing mappings, unshared candidates, volatile rmap items, skipped pages, zero-page mappings, stable-node chains, and duplicate stable nodes.
- Runs the `ksmd` kernel thread, which walks mergeable VMAs, hashes and compares anonymous pages, merges identical pages, and rebuilds unstable trees after full scans.
- Implements the stable tree for write-protected KSM pages and the unstable tree for candidate pages whose checksum remains stable across scans.
- Supports stable-node chains/dups to cap reverse-map list length per KSM page while allowing multiple KSM pages with identical content.
- Handles KSM page creation by write-protecting anonymous pages, replacing PTEs with KSM pages or KSM-placed zero pages, and updating rmap/accounting.
- Handles unmerge paths through `break_ksm()`, `ksm_disable()`, `ksm_madvise(... MADV_UNMERGEABLE)`, and sysfs `run=2`.
- Exposes KSM entry points used by the wider MM: `ksm_vma_flags()`, `ksm_enable_merge_any()`, `ksm_disable_merge_any()`, `ksm_disable()`, `ksm_madvise()`, `__ksm_enter()`, `__ksm_exit()`, `ksm_might_need_to_copy()`, `rmap_walk_ksm()`, `collect_procs_ksm()`, and `folio_migrate_ksm()`.
- Provides `/sys/kernel/mm/ksm` controls and statistics when `CONFIG_SYSFS` is enabled.

Important behavior:
- KSM eligibility excludes shared/may-share VMAs, hugetlb, droppable, special VMAs, DAX mappings, and architecture-specific incompatible flags.
- `MADV_MERGEABLE` registers the `mm` with KSM on first use and marks compatible VMAs with `VM_MERGEABLE`.
- `MMF_VM_MERGE_ANY` enables automatic mergeability for all compatible VMAs in an `mm`; `ksm_vma_flags()` applies it to newly created VMAs.
- `scan_get_next_rmap_item()` is the scanner cursor: it walks mergeable VMAs, finds anonymous pages through a page-table walk, allocates or reuses sorted `ksm_rmap_item` entries, prunes stale rmap items, and advances across mms.
- `cmp_and_merge_page()` is the central merge decision path: it handles existing KSM pages, checksum stability, zero-page merging, stable-tree lookup, unstable-tree lookup/insert, two-page promotion, and stable-tree append.
- Stable-tree lookup uses page content comparison, stale-node pruning via the KSM page mapping back-pointer, NUMA tree placement checks, and max-sharing enforcement.
- The unstable tree is reset each full scan because candidate pages are not write-protected and their content ordering can become stale.
- Smart scanning ages repeatedly unmergeable candidates and skips them for increasing scan intervals while still always processing existing KSM pages.
- KSM pages deliberately avoid holding permanent page references from stable nodes; `ksm_get_folio()` validates the page through the folio mapping tag and removes stale nodes when the page has gone away.
- `write_protect_page()` clears writable/dirty PTE state, handles anon-exclusive sharing, checks mapcount/refcount to avoid racing direct I/O or pins, and records the original PTE for later replacement.
- `replace_page()` swaps an anonymous PTE to a KSM page or marked zero-page PTE, updates anon rmap and mm counters, flushes cache/TLB state, and drops the old folio mapping.
- Reverse-map walking for KSM pages first visits the tracked originating VMAs and then searches forked VMAs sharing the anon_vma.
- Memory hotremove blocks KSM tree scans while memory is going offline and prunes stable nodes whose PFNs fall in an offline range.
- Sysfs controls include `run`, `sleep_millisecs`, `pages_to_scan`, `merge_across_nodes`, `use_zero_pages`, `max_page_sharing`, `smart_scan`, stable-chain pruning, and scan-time advisor settings.
- The scan-time advisor adjusts `pages_to_scan` based on observed scan duration, target scan time, and estimated CPU cost.

Dependencies:
- Core MM: VMAs, anon_vma, page tables, folios, rmap, swap, migration, memory failure, THP splitting, mmu notifiers, TLB/cache flushing, memcg charging, and mm flags.
- Data structures: RB trees, hlist/list primitives, mm-slot helpers, hashtable for `mm` lookup, slab caches.
- Kernel services: kthread/freezer, wait queues, sysfs, memory hotplug notifier, procfs helpers, tracepoints, xxhash, scheduler runtime accounting.
- Public behavior is tightly connected to `madvise.c` for `MADV_MERGEABLE`/`MADV_UNMERGEABLE` and to fork/mmap/exit paths through KSM mm flags.

Notable risks:
- Correctness relies on subtle lock ordering across mmap locks, VMA locks, page-table locks, anon_vma locks, folio locks, `ksm_thread_mutex`, and `ksm_mmlist_lock`.
- Stable nodes intentionally do not pin KSM pages, so stale-node detection depends on the folio mapping tag and memory-ordering with migration.
- Stable-node chain collapse, migration replacement, and duplicate insertion update RB-tree and hlist state in-place; bugs here would corrupt KSM reverse mapping.
- `break_ksm()` can fail with `-ENOMEM` while unmerging, leaving KSM pages for later retry and preventing `VM_MERGEABLE` from being cleared.
- KSM-placed zero pages are tracked via dirty special PTEs and separate accounting, which requires teardown paths to preserve the convention.
- Smart-scan skip state trades CPU for delayed deduplication and can leave candidates untried for several full scans.
- Changing `merge_across_nodes` or `max_page_sharing` is refused while stable pages remain because the stable tree layout/accounting cannot be safely retuned in place.
