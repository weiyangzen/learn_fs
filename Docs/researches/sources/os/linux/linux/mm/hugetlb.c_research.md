# File Research: sources/os/linux/linux/mm/hugetlb.c

## Purpose

`hugetlb.c` is the core Linux HugeTLB implementation. It manages huge page hstates, reservations, subpools, allocation and freeing, page-table installation and teardown, faults, copy-on-write, migration/isolation, PMD page-table sharing, boot-time huge page setup, runtime pool resizing, and accounting hooks used by hugetlbfs, SysV shared memory, memory hotplug, userfaultfd, cgroups, memcg, NUMA policy, and MMU notifier users.

## Major Responsibilities

- Maintain global hstate state in `hstates[]`, including per-node free lists, active lists, persistent page counts, surplus counts, reservation counts, demotion targets, and resize locks.
- Implement hugetlbfs reservation maps (`struct resv_map` and `struct file_region`) for shared and private mappings, including placeholder/cache handling for non-sleeping reservation updates.
- Enforce subpool limits/minimums through `hugepage_subpool_get_pages()` and `hugepage_subpool_put_pages()`.
- Allocate, free, enqueue, dequeue, dissolve, replace, demote, isolate, and migrate hugetlb folios.
- Coordinate with HugeTLB Vmemmap Optimization (HVO), including deferred freeing when vmemmap restoration cannot use sleeping allocation context.
- Handle boot-time huge page command-line parsing, memblock/gigantic-page allocation, parallel buddy allocation, hstate initialization, and final reporting.
- Implement HugeTLB VM operations, page-table copying/moving/unmapping, protection changes, userfaultfd population, and fault handling.
- Support PMD page-table sharing for compatible shared hugetlb mappings and explicit unsharing before truncation, zap, mremap, or split-sensitive operations.
- Export memory information, total huge page count, and sysfs/sysctl-facing pool resize helpers.

## Reservation and Subpool Model

The file uses two reservation layers. The global hstate has `resv_huge_pages`, while hugetlbfs inodes may have a `hugepage_subpool` with optional maximum and minimum reservation constraints. `hugepage_new_subpool()` pre-charges minimum reservations, `hugepage_put_subpool()` releases the subpool when its references and usage drop to zero, and the get/put helpers return the amount by which global reservations must be adjusted.

Reservation maps are ordered lists of `file_region` ranges. Shared mappings record offsets that have reservations; private mappings invert the meaning and record consumed reservations. The main helpers are:

- `region_chg()`: counts missing reservation ranges and preallocates file-region descriptors.
- `region_add()`: commits a prior change and coalesces adjacent regions with matching cgroup uncharge metadata.
- `region_abort()`: cancels a pending `region_chg()`.
- `region_del()`: removes, trims, or splits reservation regions and uncharges reservation cgroups.
- `region_count()`: counts reserved overlap for close/unmap accounting.

Private VMA reservation ownership is encoded in low bits of `vm_private_data` with `HPAGE_RESV_OWNER` and `HPAGE_RESV_UNMAPPED`. `hugetlb_dup_vma_private()`, `clear_vma_resv_huge_pages()`, and `fixup_hugetlb_reservations()` handle fork and mremap cases where reservation ownership must not be inherited blindly.

## VMA Locks and Fault Serialization

HugeTLB has an extra VMA-level lock abstraction. Shared mappings allocate a `struct hugetlb_vma_lock` in `vm_private_data`; private mappings use the reservation map's `rw_sema` when the VMA owns the map. Read/write lock helpers synchronize page faults, truncation, PMD sharing, zap, and VMA split/unshare paths.

Faults on the same logical file page are also serialized through `hugetlb_fault_mutex_table`, hashed by mapping and huge-page offset. This avoids spurious allocation failures when multiple CPUs race to instantiate the same huge page.

## Allocation and Freeing

Free persistent huge pages live on per-node `h->hugepage_freelists`; allocated pages live on `h->hugepage_activelist`. `enqueue_hugetlb_folio()` moves a frozen folio to a free list and updates free counters. `dequeue_hugetlb_folio_*()` selects free pages according to NUMA policy, cpuset constraints, long-term pin suitability, hardware poison state, and page isolation state.

Fresh folios come from either the buddy allocator or gigantic-page contiguous allocation/CMA paths:

- `alloc_buddy_frozen_folio()` wraps `__alloc_frozen_pages()` and tracks per-node no-retry state for bulk pool growth.
- `alloc_gigantic_frozen_folio()` tries HugeTLB CMA first and then `alloc_contig_frozen_pages()` unless CMA-only allocation is configured.
- `alloc_fresh_hugetlb_folio()` initializes the folio and applies HVO.
- `alloc_surplus_hugetlb_folio()` grows the surplus pool within `nr_overcommit_huge_pages`.
- `alloc_hugetlb_folio()` is the fault-time allocator that combines reservation map state, subpool accounting, hugetlb cgroup reservation/usage charges, hstate free-list dequeue, surplus allocation fallback, memcg charging, rmap/stat setup, and reservation commit/rollback.

Freeing flows through `free_huge_folio()`, which restores reservations when needed, uncharges hugetlb cgroups and memcg, updates `NR_HUGETLB`, returns non-surplus pages to free lists, and frees temporary/surplus pages back to the lower allocator. HVO-aware freeing uses `hugetlb_vmemmap_restore_folio()` or bulk restoration before clearing the hugetlb flag and releasing pages. Atomic contexts can defer freeing through `hpage_freelist` and `free_hpage_work`.

## Pool Resizing, Surplus Pages, and Demotion

`set_max_huge_pages()` is the runtime pool resizing engine used by sysfs and sysctl. It serializes with `h->resize_lock`, flushes deferred free work, converts surplus pages back to persistent pages when growing, allocates fresh pool pages in node-rotating order, frees excess free pages when shrinking, and marks still-in-use excess pages as surplus.

Reservation growth uses `gather_surplus_pages()` to temporarily allocate surplus pages so reservations can succeed, then commits or rolls them back. `return_unused_surplus_pages()` releases unused reservation-backed surplus pages.

Demotion lets free huge pages in a larger hstate be split into smaller hstate pages. `demote_pool_huge_page()` selects free source folios, `demote_free_hugetlb_folios()` restores source vmemmap, splits page owner/allocation tags and compound metadata, preserves CMA state, initializes child hugetlb folios, and adds them to the destination hstate. Hstate initialization selects a default `demote_order` when a smaller hstate exists and runtime/CMA constraints allow it.

## Boot-Time Setup

HugeTLB command-line handling is staged: early parameters are copied into an init buffer by `hugetlb_add_param()` and consumed later by `hugetlb_parse_params()` after valid huge page sizes are known. Supported parameters include `hugepages=`, `hugepagesz=`, `default_hugepagesz=`, and `hugepage_alloc_threads=`.

Gigantic pages are allocated early through memblock or HugeTLB CMA and placed in `huge_boot_pages` until `gather_bootmem_prealloc()` converts them into normal hugetlb folios after memmap setup. Non-gigantic boot pages are allocated from the buddy allocator, potentially in parallel through padata. Boot initialization also validates zone boundaries, initializes tail vmemmap pages when HVO did not pre-optimize, sets pageblock migratetypes, updates managed page counts, and registers sysfs, cgroup files, sysctl handlers, and the fault mutex table.

## Page Tables and VM Operations

`hugetlb_vm_ops` supplies open/close, split validation, pagesize reporting, and a BUG fault method because normal VM faults must be routed to `hugetlb_fault()`. VMA open/close manage reservation map references and shared VMA locks; close releases unused private reservations and subpool/global reservation accounting.

Page-table helpers include:

- `make_huge_pte()` and writable variants for architecture-adjusted huge PTE creation.
- `copy_hugetlb_page_range()` for fork, including COW write-protection, rmap duplication, migration/hwpoison/marker entries, userfaultfd write-protect preservation, and early COW when anon rmap duplication fails.
- `move_hugetlb_page_tables()` for mremap-style relocation with MMU notifier and TLB gather sequencing.
- `__unmap_hugepage_range()` and `unmap_hugepage_range()` for zap/truncate/unmap, including PMD unsharing, dirtying, rmap removal, UFFD-WP marker preservation, reservation restoration for private anonymous pages, and TLB batching.
- `hugetlb_change_protection()` for mprotect/userfaultfd write-protect changes over present PTEs, migration entries, hwpoison entries, and markers.

## Fault Handling

`hugetlb_fault()` handles all HugeTLB faults. It hashes and takes the per-page fault mutex, takes the VMA lock, allocates/looks up the huge PTE, and dispatches to:

- `hugetlb_no_page()` for missing PTEs, page-cache lookup, userfaultfd missing/minor events, fresh allocation, page-cache insertion, anonymous rmap setup, and optional immediate write fault handling.
- `hugetlb_wp()` for write-protect/COW/unshare faults, including shared mapping write enable, exclusive anonymous page reuse, private-owner COW reservation bypass, child unmapping on owner COW failure, anon preparation, folio copy, MMU notifier invalidation, and reservation rollback.
- migration-entry wait and hwpoison error handling for non-present entries.
- userfaultfd write-protect resolution before COW.

The fault path is careful about lock dropping. Userfaultfd handling drops the VMA lock and fault mutex because it can drop `mmap_lock`. COW allocation drops the page-table lock around allocation/copying, then revalidates the PTE before installation.

## Userfaultfd Population

Under `CONFIG_USERFAULTFD`, `hugetlb_mfill_atomic_pte()` supports UFFDIO_COPY, UFFDIO_CONTINUE, UFFDIO_POISON, and write-protect population. It can allocate the final reservation-consuming folio, fall back to a temporary folio for copying outside `mmap_lock`, insert shared pages into the hugetlbfs page cache, install poison or write-protect markers, reject existing mappings, handle hwpoison, and update rmap/mm counters and migratability state.

## PMD Sharing

When `CONFIG_HUGETLB_PMD_PAGE_TABLE_SHARING` is enabled, compatible shared VMAs can share PMD page-table pages for PMD-sized huge pages. `want_pmd_share()` checks VMA shareability, VMA lock presence, userfaultfd restrictions, and PUD alignment. `huge_pmd_share()` searches the file mapping's interval tree for a compatible VMA and installs a shared PMD table while holding `i_mmap_rwsem`.

Unsharing uses `huge_pmd_unshare()` / `__huge_pmd_unshare()` to clear the PUD entry, decrement PMD accounting, and hand the shared page table to TLB gather. `huge_pmd_unshare_flush()` synchronizes walkers before `i_mmap_rwsem` is dropped. `adjust_range_if_pmd_sharing_possible()` widens invalidation ranges to PUD boundaries when needed.

## Migration, Memory Hotplug, and Poison

The file provides free-page dissolving and allocated-page isolation:

- `dissolve_free_hugetlb_folio()` and `dissolve_free_hugetlb_folios()` remove free huge pages from the pool for memory hotplug.
- `replace_free_hugepage_folios()` replaces free huge pages in a PFN range.
- `isolate_or_dissolve_huge_folio()` either isolates an in-use folio or allocates a replacement and dissolves a free folio.
- `folio_isolate_hugetlb()` and `folio_putback_hugetlb()` manage migration isolation references and active-list membership.
- `move_hugetlb_state()` transfers cgroup state, owner migration reason, temporary/surplus node state, and migratability after migration.
- `get_hwpoison_hugetlb_folio()` safely obtains references for hwpoison/unpoison handling.

## Integration Points and Invariants

This file is central to HugeTLB correctness. Important invariants include holding `hugetlb_lock` for hstate counters/lists and cgroup folio pointer updates, using reservation-map `region_chg`/`region_add`/`region_abort` as a transaction, preserving VMA locks around shared PMD page-table walks, restoring HVO vmemmap before freeing pages to the buddy allocator, and carefully pairing hugetlb cgroup reservation references with file-region or resv-map lifetime.
