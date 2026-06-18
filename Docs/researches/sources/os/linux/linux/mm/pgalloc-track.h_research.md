# File Research: sources/os/linux/linux/mm/pgalloc-track.h

## Purpose

`mm/pgalloc-track.h` provides small inline helpers for allocating page-table levels while recording which upper-level page-table entry was modified. It is used by page-table manipulation paths that need to return a `pgtbl_mod_mask` to callers.

## Helpers

Under `CONFIG_MMU`, the file defines:

- `p4d_alloc_track(mm, pgd, address, mod_mask)`: allocates a missing P4D under a PGD and sets `PGTBL_PGD_MODIFIED`.
- `pud_alloc_track(mm, p4d, address, mod_mask)`: allocates a missing PUD under a P4D and sets `PGTBL_P4D_MODIFIED`.
- `pmd_alloc_track(mm, pud, address, mod_mask)`: allocates a missing PMD under a PUD and sets `PGTBL_PUD_MODIFIED`.

It also defines `pte_alloc_kernel_track(pmd, address, mask)`, which allocates a kernel PTE table if the PMD is none and sets `PGTBL_PMD_MODIFIED`.

## Behavior

Each helper checks whether the relevant upper-level entry is absent. If allocation fails, it returns `NULL`; otherwise it sets the appropriate modification bit and returns the next-level offset pointer. Existing entries are not marked modified.

## Dependencies and Assumptions

The helpers rely on the normal architecture page-table allocation primitives (`__p4d_alloc`, `__pud_alloc`, `__pmd_alloc`, `__pte_alloc_kernel`) and standard offset helpers (`p4d_offset`, `pud_offset`, `pmd_offset`, `pte_offset_kernel`). They do not introduce their own locking; callers must satisfy the same locking rules required by the underlying page-table allocation path.

## Filesystem/MM Relevance

These helpers are infrastructure for page-table modification accounting. They are relevant to memory-management paths that need to know whether a page table was materially changed, such as mapping-installation logic, mmu notifier synchronization, or architecture-specific TLB/cache maintenance decisions.
