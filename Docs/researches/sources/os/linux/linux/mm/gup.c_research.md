# File Research: sources/os/linux/linux/mm/gup.c

## Purpose

`gup.c` is the Linux memory-management implementation of get-user-pages and pin-user-pages APIs. It translates user virtual address ranges into referenced `struct page` pointers, optionally faults pages into existence, and distinguishes ordinary references (`FOLL_GET`) from DMA-style pins (`FOLL_PIN`). It also contains the fast lockless page-table walker, slow faulting path, long-term pin migration checks, page/folio unpin helpers, prefault helpers, and memfd folio pinning support.

## Major Responsibilities

- Implement public GUP/PUP entry points: `get_user_pages*()`, `pin_user_pages*()`, fast-only variants, remote variants, and unlocked variants.
- Walk page tables through PTE/PMD/PUD levels and follow normal pages, huge PMDs/PUDs, zero pages, gate pages, and special PFN mappings.
- Fault missing or insufficiently permitted mappings with `handle_mm_fault()` when the caller allows the slow path.
- Enforce VMA access rules, architecture access permissions, `FOLL_FORCE`, write/COW semantics, secretmem rejection, and DAX/long-term restrictions.
- Track DMA pins separately from ordinary page references using folio pincounts or `GUP_PIN_COUNTING_BIAS`.
- Provide unpin APIs that optionally dirty pages and collapse repeated pages from the same folio for efficient refcount updates.
- Support long-term pins by rejecting or migrating movable/unpinnable folios before returning them pinned.
- Provide prefault helpers such as `fault_in_readable()`, `fault_in_writeable()`, `fault_in_safe_writeable()`, `populate_vma_page_range()`, `faultin_page_range()`, and `__mm_populate()`.
- Pin folios belonging to memfd-backed shmem or hugetlb files through `memfd_pin_folios()`.

## Reference and Pin Accounting

The central helpers are:

- `try_get_folio()`: safely raises a folio refcount after checking that the original page still belongs to the same folio.
- `try_grab_folio()`: implements `FOLL_GET` or `FOLL_PIN` behavior for slow paths.
- `try_grab_folio_fast()`: fast-path version used with interrupts disabled.
- `gup_put_folio()`: releases either ordinary references or DMA pins.

`FOLL_PIN` differs from `FOLL_GET`: zero folios are deliberately not pinned, large folios with a dedicated pincount update `_pincount`, and smaller folios encode pins by adding `GUP_PIN_COUNTING_BIAS` to the normal refcount. Pin acquisition and release update `NR_FOLL_PIN_ACQUIRED` and `NR_FOLL_PIN_RELEASED`.

Debug checks in `sanity_check_pinned_pages()` verify that anonymous pinned pages remain exclusive, because once a page is pinned the kernel cannot safely convert it into a shared anonymous mapping. The file also rejects PCI P2PDMA pages unless `FOLL_PCI_P2PDMA` is explicitly allowed.

## Unpin and Dirtying APIs

Exported release helpers include:

- `unpin_user_page()`
- `unpin_folio()`
- `unpin_user_pages()`
- `unpin_user_folio()`
- `unpin_folios()`
- `unpin_user_pages_dirty_lock()`
- `unpin_user_page_range_dirty_lock()`
- `folio_add_pin()`
- `folio_add_pins()`

Dirtying variants group adjacent pages that belong to the same folio, mark clean folios dirty under the folio lock when requested, and then release the corresponding number of pins. The non-dirty unpin path also groups repeated folios to avoid redundant accounting. `gup_fast_unpin_user_pages()` is a fast-path rollback helper and intentionally skips some debug checks because it can run after a fork race invalidated exclusivity assumptions.

## Slow GUP Path

The slow path begins in `__get_user_pages_locked()` and calls `__get_user_pages()`. It requires or acquires `mmap_lock`, optionally allows the fault handler to drop it, and loops over VMAs and page-table mappings until the requested range is processed or an error occurs.

Important slow-path helpers:

- `gup_vma_lookup()`: VMA lookup with diagnostics for historical stack-growth behavior.
- `check_vma_flags()`: rejects VM_IO, VM_PFNMAP, secretmem, incompatible anonymous/file mappings, shadow stacks, FSDAX long-term pins, and permission violations.
- `follow_page_mask()`: top-level page-table follower.
- `follow_p4d_mask()`, `follow_pud_mask()`, `follow_pmd_mask()`, `follow_page_pte()`: page-table level walkers.
- `follow_huge_pud()` and `follow_huge_pmd()`: huge leaf handlers.
- `faultin_page()`: converts GUP flags to `FAULT_FLAG_*` and invokes `handle_mm_fault()`.
- `get_gate_page()`: handles architecture gate/vDSO-like pages.

`__get_user_pages()` can return partial success. If a page is missing or a read-only mapping must be unshared for `FOLL_PIN`, it calls `faultin_page()` and retries. It handles `-EMLINK` as an unshare request, `-EEXIST` for PFN mappings without `struct page`, and copies subpages of large folios into the caller's page array while taking the extra references needed for the whole range.

## Write, COW, and Long-Term Safety

The file is careful about write access. `can_follow_write_common()`, `can_follow_write_pte()`, `can_follow_write_pmd()`, and `can_follow_write_pud()` allow `FOLL_FORCE` only for private COW-capable mappings where the anonymous page is exclusive and no soft-dirty or userfaultfd write-protect condition requires a real write fault.

`writable_file_mapping_allowed()` prevents the most problematic case: a long-term `FOLL_PIN | FOLL_WRITE` against a file-backed mapping that needs dirty tracking. That scenario can bypass filesystem write-notify semantics and silently dirty data through the direct kernel mapping.

Long-term pins are routed through `__gup_longterm_locked()`. When `FOLL_LONGTERM` is present, pages are first pinned, then `check_and_migrate_movable_pages()` verifies that the resulting folios are long-term pinnable. If not, `collect_longterm_unpinnable_folios()` isolates movable folios or identifies device-coherent folios, and `migrate_longterm_unpinnable_folios()` unpins and migrates them. Successful migration returns `-EAGAIN` internally so the full range is pinned again.

## Fast GUP Path

`gup_fast_fallback()` drives the fast path. It validates the user range, tries `gup_fast()`, and only falls back to slow GUP if the fast path did not pin all pages and the caller did not request `FOLL_FAST_ONLY`.

Fast GUP is compiled under `CONFIG_HAVE_GUP_FAST`. It disables interrupts while walking page tables so page-table pages cannot be freed underneath the walker. The hierarchy is:

- `gup_fast_pgd_range()`
- `gup_fast_p4d_range()`
- `gup_fast_pud_range()`
- `gup_fast_pmd_range()`
- `gup_fast_pte_range()`
- `gup_fast_pmd_leaf()`
- `gup_fast_pud_leaf()`

Fast PTE handling pins the folio first, then verifies that both the higher-level entry and the PTE still match. If anything changed, the pin is released and the caller falls back. Fast GUP rejects PROT_NONE, inaccessible entries, special PTEs, unsafe long-term writable file-backed folios, secretmem folios, and mappings requiring anonymous unsharing.

For `FOLL_PIN`, `gup_fast()` also samples `current->mm->write_protect_seq`; if fork write-protection races with a DMA pin, fast-pinned pages are unpinned and the slow path is used.

## Public APIs and Return Conventions

Public APIs validate external flags through `is_valid_gup_args()`, which blocks internal-only flags, enforces `FOLL_GET` and `FOLL_PIN` mutual exclusion, requires `pages` for get/pin operations, and rejects invalid `FOLL_LONGTERM` combinations.

Key exported entry points:

- `get_user_pages_remote()`
- `get_user_pages()`
- `get_user_pages_unlocked()`
- `get_user_pages_fast_only()`
- `get_user_pages_fast()`
- `pin_user_pages_remote()`
- `pin_user_pages()`
- `pin_user_pages_unlocked()`
- `pin_user_pages_fast()`
- `fixup_user_fault()`
- `get_dump_page()`

Most APIs return the number of pages pinned/referenced, possibly less than requested, or a negative error if no pages were obtained. Some pin APIs return `0` on argument-validation failure paths where older API behavior expects that convention.

## Prefault and Population Helpers

The file also provides user-memory prefault helpers used by copy loops, mlock, MAP_POPULATE, and `MADV_POPULATE_*`.

- `fault_in_writeable()` and `fault_in_readable()` probe userspace with unsafe access helpers and return the number of bytes not faulted in.
- `fault_in_subpage_writeable()` adds sub-page permission probing for cases such as arm64 MTE.
- `fault_in_safe_writeable()` resolves write faults via `fixup_user_fault()` without writing to the target memory.
- `populate_vma_page_range()` faults in a single VMA range and respects `VM_LOCKONFAULT`, access permissions, and COW behavior.
- `faultin_page_range()` is the MADV_POPULATE-oriented helper with stricter error reporting.
- `__mm_populate()` walks VMAs without an initial `mmap_lock` and faults in eligible ranges.

## memfd Folio Pinning

`memfd_pin_folios()` pins folios from shmem or hugetlb-backed memfd files over a byte range. It looks up contiguous page-cache folios with `filemap_get_folios_contig()`, allocates missing folios through `memfd_alloc_folio()`, records the offset into the first folio, and then runs long-term migration checks using the folio-oriented migration wrapper. Callers must release the returned folios with `unpin_folios()` or `unpin_folio()`.

## Integration Points

This file sits at the boundary between the VM, filesystems, DMA, core dumping, futex-style fault fixups, memory migration, hugetlb, transparent huge pages, secretmem, shmem, memfd, and architecture page-table code. Its invariants are consumed broadly: DMA users rely on `FOLL_PIN` accounting, filesystems rely on long-term write restrictions, fork relies on write-protect sequence detection, and mmu/page-table code relies on the fast walker respecting TLB and page-table lifetime rules.
