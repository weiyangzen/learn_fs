# File Research: sources/os/linux/linux/mm/sparse-vmemmap.c

## Purpose
Implements SPARSEMEM VMEMMAP backing for `struct page` arrays. It allocates memory and page tables for the virtual memmap, supports base-page and huge-PMD mappings, handles alternate memmap storage for device memory, optimizes hugetlb/devmap compound-page tails, and supports memory hotplug section activation/removal.

## Main Interfaces
- Allocation helpers: `vmemmap_alloc_block()`, `vmemmap_alloc_block_buf()`, `altmap_alloc_block_buf()`.
- Page-table population: `vmemmap_pgd_populate()`, `vmemmap_p4d_populate()`, `vmemmap_pud_populate()`, `vmemmap_pmd_populate()`, `vmemmap_pte_populate()`.
- Mapping entry points: `vmemmap_populate_basepages()`, `vmemmap_populate_hugepages()`, `__populate_section_memmap()`.
- Hugetlb optimized vmemmap support: `vmemmap_wrprotect_hvo()`, `vmemmap_populate_hvo()`.
- Sparse section state: `sparse_init_subsection_map()`, `sparse_add_section()`, `sparse_remove_section()`.
- Hotplug section state: `online_mem_sections()`, `offline_mem_sections()`.

## Control Flow
Early boot allocations use memblock via `memmap_alloc()`, while later allocation uses `alloc_pages_node()` with retry/no-warn semantics. VMEMMAP population walks the kernel page-table hierarchy and installs PTEs for `struct page` backing, optionally using a supplied physical page frame when deduplicating tail page structs.

Hugepage population first tries PMD-sized vmemmap backing through arch hooks, then falls back to base PTE mappings. Hugetlb optimized vmemmap maps head page structs normally and reuses one tail `struct page` backing page for the rest. Device compound-page population similarly maps head/tail pages and reuses tail backing across sections when appropriate.

Memory hotplug activates subsections by allocating section usage metadata, setting subsection bitmaps, populating memmap backing unless an early section can be reused, poisoning uninitialized page structs, and marking the section present. Removal clears subsection bits, frees vmemmap backing when safe, and releases non-boot usage metadata via RCU.

## State And Synchronization
Uses `mem_section->usage->subsection_map`, `SECTION_HAS_MEM_MAP`, `SECTION_IS_ONLINE`, early-section flags, and per-zone `vmemmap_tails`. PTE page references are incremented for specific ZONE_DEVICE compound reuse paths so later page-table freeing pairs with `put_page_testzero()`.

## Dependencies
Depends on sparsemem section helpers, memblock/slab allocation, kernel page-table APIs, altmap/device pagemap metadata, hugetlb vmemmap optimization, memory hotplug, and architecture-provided `vmemmap_populate()`, `vmemmap_set_pmd()`, `vmemmap_check_pmd()`, and `vmemmap_free()` behavior.

## Risks And Review Focus
- Altmap sizing/alignment failures are treated as hard failures in hugepage paths.
- Tail-page deduplication relies on strict population ordering and correct page ref ownership.
- Hotplug subsection bitmap transitions must stay consistent with `valid_section()` and RCU freeing of usage maps.
- Early sections are special because their memmap is assumed fully populated and boot-allocated usage maps may be shared.
