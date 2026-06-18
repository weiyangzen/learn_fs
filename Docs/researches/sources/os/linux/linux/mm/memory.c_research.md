# File Research: sources/os/linux/linux/mm/memory.c

## Role

Linux core virtual-memory mapping and page-fault implementation. This file owns the generic machinery for page-table allocation and teardown, fork-time page-table copying, PTE/PMD/PUD fault dispatch, anonymous and file-backed fault completion, copy-on-write, swap-in, NUMA hinting faults, userfaultfd marker handling, PFN/page insertion APIs for drivers, page-table range application, remote process memory access, and helper routines for large-folio user copying/zeroing.

It sits at the center of the `mm/` subsystem: architecture page-fault handlers eventually enter `handle_mm_fault()`, VFS and filesystems rely on its mapping invalidation helpers, drivers use its PFN/page insertion exports, and fork/exit/unmap paths use its page-table copy/zap/free routines.

## Key Behavior

- Registers `kernel.randomize_va_space` and supports `norandmaps`, with the default depending on `CONFIG_COMPAT_BRK`.
- Tracks `highest_memmap_pfn` and exposes `mm_trace_rss_stat()` for RSS tracing.
- Frees page-table levels through `free_pgd_range()` / `free_pgtables()`, including `floor` and `ceiling` boundary logic for shared upper-level tables and `mmu_gather` TLB batching.
- Allocates and installs page-table pages with `pmd_install()`, `__pte_alloc()`, `__pte_alloc_kernel()`, and folded-level allocation helpers `__p4d_alloc()`, `__pud_alloc()`, and `__pmd_alloc()`.
- Classifies PTE/PMD/PUD PFNs through `vm_normal_page()`, `vm_normal_folio()`, and huge-leaf variants, distinguishing normal refcounted pages from special zero, PFNMAP, MIXEDMAP, and architecture-special entries.
- Emits rate-limited diagnostics for corrupted or invalid page-table mappings via `print_bad_page_map()` and taints the kernel with `TAINT_BAD_PAGE`.
- Copies page-table ranges for fork in `copy_page_range()`, including COW write-protection, RSS accounting, swap entry duplication, migration entries, device-private/exclusive entries, PTE markers, large-folio batching, pinned-page COW copying, MMU notifier invalidation, and swap retry-table allocation.
- Zaps and unmaps ranges through `zap_vma_range_batched()`, `zap_vma_range()`, `unmap_vmas()`, and lower-level PTE/PMD/PUD/PGD walkers, preserving userfaultfd write-protect markers when required and optionally reclaiming empty PTE tables under `CONFIG_PT_RECLAIM`.
- Provides `zap_vma_for_reaping()` for the OOM reaper, using nonblocking MMU notifier invalidation and refusing work that would block.
- Handles hugetlb unmap setup/teardown, huge PMD/PUD zapping, PMD sharing synchronization, and TLB flush ordering in the generic zap path.
- Exposes driver/user mapping APIs: `vm_insert_page()`, `vm_insert_pages()`, `vm_map_pages()`, `vm_map_pages_zero()`, `vmf_insert_pfn_prot()`, `vmf_insert_pfn()`, `vmf_insert_page_mkwrite()`, `vmf_insert_mixed()`, `vmf_insert_mixed_mkwrite()`, `remap_pfn_range()`, `vm_iomap_memory()`, and mmap-action prepare/complete helpers.
- Validates driver-inserted pages, disallowing anonymous, typed, invalid-refcount, and unsafe zero-page insertions; converts eligible VMAs to `VM_MIXEDMAP` or PFN remap flags as needed.
- Implements raw PFN remapping with page-table population, cache-mode setup, optional PFNMAP tracking, COW `vm_pgoff` compatibility, partial-failure zapping, and `pfn_modify_allowed()` enforcement.
- Implements `apply_to_page_range()` and `apply_to_existing_page_range()` for iterating leaf PTEs, optionally creating missing page tables and syncing architecture kernel mappings when page-table modifications require it.
- Implements write-protect fault handling through `do_wp_page()`, with paths for userfaultfd write-protect, shared file write-notify, PFNMAP/MIXEDMAP `pfn_mkwrite`, anonymous reuse, large anonymous folio reuse, COW copying, KSM COW accounting, MMU notifier invalidation, and careful TLB/rmap ordering.
- Unmaps file-backed mappings for truncate/invalidate via `unmap_mapping_folio()`, `unmap_mapping_pages()`, and `unmap_mapping_range()`, using the address-space interval tree and `zap_details` to choose whether private COW pages are skipped.
- Handles non-present PTE faults in `do_swap_page()`, including swap cache lookup/readaround, synchronous swap IO, THP-sized swap-in where possible, KSM copy-on-read, hwpoison, migration entries, device-private `migrate_to_ram`, device-exclusive restore, PTE markers, swap exclusivity, memcg charge, swapcache release, arch swap metadata restore, and follow-up COW for write faults.
- Handles anonymous faults in `do_anonymous_page()`, using the shared zero page for eligible read faults and allocating order-0 or multi-page anonymous folios for writes, while preserving userfaultfd missing and write-protect semantics.
- Completes file and anonymous faults with `finish_fault()`, `set_pte_range()`, and `do_set_pmd()`, including large-folio PTE batching, PMD-sized file THP mapping, i-size SIGBUS protection for non-shmem files, RSS accounting, rmap insertion, cache flushes, and MMU cache updates.
- Provides read fault-around through `do_fault_around()` and debugfs `fault_around_bytes`, calling filesystem `->map_pages()` within VMA/PTE boundaries before falling back to `->fault()`.
- Dispatches file faults through `do_read_fault()`, `do_cow_fault()`, and `do_shared_fault()`, integrating filesystem `->fault()`, `->page_mkwrite()`, COW preallocation, dirty throttling, and locked-folio cleanup.
- Handles NUMA hinting faults in `do_numa_page()`, restoring protnone mappings, collecting task/folio locality signals, rebuilding large-folio PTE ranges, and invoking misplaced-folio migration.
- Coordinates transparent hugepage and huge-leaf faults through `create_huge_pmd()`, `wp_huge_pmd()`, `create_huge_pud()`, `wp_huge_pud()`, huge NUMA paths, and split fallback when generic PTE handling is required.
- Exposes the primary architecture-facing fault entry `handle_mm_fault()`, sanitizing flags, checking architecture access permission, entering memcg user-fault OOM handling, selecting hugetlb vs generic fault handling, supporting per-VMA locks, suppressing OOM for droppable mappings, and accounting major/minor faults.
- Exposes PFNMAP lookup with `follow_pfnmap_start()` / `follow_pfnmap_end()`, supporting PTE, PMD, and PUD leaf mappings while holding the relevant page-table lock and warning callers about stale PFN security hazards.
- Implements `generic_access_phys()` for accessing IO/PFNMAP VMAs through temporary `ioremap_prot()` after validating that the PFN/protection did not change across remapping.
- Implements remote memory helpers `access_remote_vm()`, `access_process_vm()`, and BPF-only `copy_remote_vm_str()`, using GUP for normal pages, VMA `->access()` for IO mappings, stack expansion where allowed, and kernel mapping/copy helpers.
- Provides debugging and safety helpers: `print_vma_addr()`, `__might_fault()`, split page-table-lock cache setup/free, and hugetlb-aware `vma_pgtable_walk_begin()` / `vma_pgtable_walk_end()`.
- Provides large-folio/hugepage user-memory helpers `folio_zero_user()`, `copy_user_large_folio()`, and `copy_folio_from_user()`, ordering subpage processing to keep the faulting subpage cache-hot and inserting reschedule points.

## Public Interfaces And Exports

Exported or externally visible interfaces include page-table teardown/allocation (`free_pgd_range()`, `free_pgtables()`, `pmd_install()`, `__pte_alloc*()`, folded-level allocators), mapping classification (`vm_normal_page*()`, `vm_normal_folio*()`), zap/unmap helpers (`zap_vma_for_reaping()`, `unmap_vmas()`, `zap_vma_range*()`, `unmap_mapping_*()`), driver insertion/remap helpers (`vm_insert_*()`, `vm_map_pages*()`, `vmf_insert_*()`, `remap_pfn_range*()`, `vm_iomap_memory()`), page-range walkers (`apply_to_page_range()`, `apply_to_existing_page_range()`), fault helpers (`__vmf_anon_prepare()`, `do_swap_page()`, `map_anon_folio_pte_nopf()`, `do_set_pmd()`, `set_pte_range()`, `finish_fault()`, `handle_mm_fault()`), PFNMAP access (`follow_pfnmap_start/end()`, `generic_access_phys()`), process memory access (`access_remote_vm()`, `access_process_vm()`, `copy_remote_vm_str()` when BPF syscall support is enabled), and large-folio copy/zero helpers.

The most important call chain for normal faults is `handle_mm_fault()` -> `__handle_mm_fault()` -> huge PMD/PUD handling or `handle_pte_fault()` -> `do_pte_missing()`, `do_swap_page()`, `do_numa_page()`, `do_wp_page()`, or access-bit update. File faults enter `do_fault()` and eventually `finish_fault()`, while anonymous faults enter `do_anonymous_page()`.

## Dependencies

Depends on the core MM model: `mm_struct`, `vm_area_struct`, folios/pages, page-table types and architecture accessors, rmap, anon_vma, KSM, swap cache and swap entries, memcg charging/OOM, LRU and multi-gen LRU hooks, hugetlb, transparent hugepages, device private/exclusive memory, DAX/FSDAX, userfaultfd, MMU notifiers, TLB gather/flush APIs, file address-space interval trees, page writeback/dirty throttling, NUMA policy/migration, perf fault counters, debugfs, BPF remote string copy support, and architecture hooks for cache/TLB/MMU metadata.

## Concurrency And Correctness Notes

- Page-table updates are protected with the appropriate PTE/PMD/PUD locks, while VMA stability comes from mmap locks or per-VMA locks depending on `FAULT_FLAG_VMA_LOCK`.
- COW and fork paths coordinate with secondary MMUs through MMU notifier ranges and `write_protect_seq`.
- Many routines intentionally revalidate PTEs after dropping locks for allocation, IO, folio locks, filesystem callbacks, or MMU notifier work.
- TLB flush ordering is critical in COW and zap paths: old mappings are cleared/flushed before rmap/mapcount changes can allow reuse.
- Device-exclusive entries rely on MMU notifiers plus folio locking to restore CPU mappings safely.
- Userfaultfd markers are preserved or dropped based on VMA type and `zap_details`, so unmap and fault paths must not treat all non-present PTEs as ordinary swap.
- Large-folio batching is used where semantics allow it, but fault handling falls back to per-page PTEs for userfaultfd, i-size boundary preservation, VMA/PTE-boundary overflow, hwpoisoned THPs, or partial swap-in constraints.
- Remote IO/PFNMAP access validates PFN/protection twice around `ioremap_prot()` to avoid copying through stale mappings.

## Research Notes

`mm/memory.c` is the generic Linux VM fault and mapping coordinator rather than a narrow page-fault file. Its main design pattern is optimistic fast-path work with strict revalidation: allocate or fault outside locks where necessary, retake the relevant page-table lock, compare the original entry, and only then commit PTE/PMD state plus rmap/RSS/memcg accounting. The file also serves as a compatibility boundary for many subsystems: filesystems provide `vm_ops`, drivers provide PFN/page mappings, architectures provide page-table and TLB primitives, and memory-management features such as userfaultfd, KSM, THP, NUMA balancing, memcg, DAX, and device-private memory all intersect here.
