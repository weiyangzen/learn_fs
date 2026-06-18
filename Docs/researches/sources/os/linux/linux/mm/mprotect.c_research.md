# File Research: sources/os/linux/linux/mm/mprotect.c

Protection-changing implementation for `mprotect`, `pkey_mprotect`, memory protection keys, and shared internal page-table protection updates.

Key responsibilities:
- Implements `mprotect`, `pkey_mprotect`, `pkey_alloc`, and `pkey_free`.
- Provides `mprotect_fixup()` for VMA flag/prot updates, VMA splitting/merging, accounting, perf notifications, and page-table protection changes.
- Exports `change_protection()` for internal callers such as NUMA balancing, soft-dirty tracking, and userfaultfd write-protect.
- Walks page tables across PTE/PMD/PUD/P4D/PGD levels, including THP, hugetlb, migration entries, device-private entries, poison/guard markers, and userfaultfd markers.
- Optimizes batches of PTE updates for large folios while respecting write, soft-dirty, uffd-wp, and anon-exclusive constraints.
- Implements pkey allocation/freeing against architecture pkey state.

Important behavior:
- Writable PTE upgrades are only done when they match what the fault handler would safely do: dirty shared PTEs, or exclusive anonymous private pages, and not soft-dirty/uffd-wp/protnone entries.
- Large anonymous folio batches may be split into sub-batches because per-page `PageAnonExclusive` can differ inside one folio.
- Nonpresent entries are adjusted for migration/device-private writable-to-readable conversion and uffd-wp set/resolve. Guard and poison markers are not converted.
- File-backed uffd-wp may require populating page tables and installing PTE markers even for `pte_none()`.
- Huge PMD/PUD entries are changed in place when range-aligned and supported, otherwise split to PTE level.
- `change_protection()` uses `PAGE_NONE` for NUMA balancing and otherwise uses `vma->vm_page_prot`; hugetlb is delegated to hugetlb-specific helpers.
- `mprotect_fixup()` rejects sealed VMAs, checks PFN permission for PROT_NONE PFN mappings, handles commit accounting when private mappings become writable, updates VMA flags/prot, and populates private locked VMAs that become writable.
- `do_mprotect_pkey()` validates alignment, growth flags, architecture protection/flag rules, pkey allocation, VMA contiguity, may-access flags, W^X policy, LSM hooks, VMA-specific `mprotect` hooks, and then performs fixups under an `mmu_gather`.

Dependencies:
- Page-table walkers and modification helpers, TLB gather, MMU notifiers, hugetlb/THP helpers, soft-dirty, userfaultfd, swap/migration/device-private entries, pkeys, LSM, map-deny-write-exec policy, VMA modification helpers, commit accounting, mlock population, and architecture protection validation.

Notable risks:
- Writable fast-upgrades must stay consistent with write-fault/COW rules or they can bypass required filesystem, uffd, soft-dirty, or COW behavior.
- Hugepage splitting/population paths can fail and require retry or error handling.
- VMA sealing blocks mprotect; callers must surface `-EPERM`.
- Accounting when adding/removing `VM_ACCOUNT` must remain paired with VMA mutation failure paths.
- `mprotect()` over multiple VMAs fails if any gap exists or if requested permissions exceed `VM_MAY*`.
