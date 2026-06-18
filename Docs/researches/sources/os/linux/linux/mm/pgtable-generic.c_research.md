# File Research: sources/os/linux/linux/mm/pgtable-generic.c

## Purpose

`mm/pgtable-generic.c` supplies generic fallback implementations for page-table operations declared in `linux/pgtable.h`. Architectures can override many of these via `__HAVE_ARCH_*` defines; this file provides the common implementation where no architecture-specific version exists.

## Bad Entry Handling

The file defines `pgd_clear_bad()`, `p4d_clear_bad()`, `pud_clear_bad()`, and `pmd_clear_bad()`. Each reports the bad entry via the architecture `*_ERROR()` macro and clears it. P4D/PUD versions are omitted when folded, while PMD remains present because PMD folding is special and PMD macros may still refer to upper levels.

## Accessed/Dirty and Flush Helpers

Generic PTE helpers include:

- `ptep_set_access_flags()`: installs a more permissive PTE when changed and flushes spurious-fault TLB state.
- `ptep_clear_flush_young()`: clears accessed/young and flushes the page if it changed.
- `ptep_clear_flush()`: clears a PTE and flushes if the old PTE was accessible.

Transparent huge page helpers, when enabled, include:

- `pmdp_set_access_flags()`
- `pmdp_clear_flush_young()`
- `pmdp_huge_clear_flush()`
- optional `pudp_huge_clear_flush()`
- `pmdp_invalidate()` and `pmdp_invalidate_ad()`
- `pmdp_collapse_flush()`

These paths enforce hugepage alignment with `VM_BUG_ON()` checks and flush the relevant PMD/PUD/TLB ranges.

## THP Page-Table Deposit/Withdraw

`pgtable_trans_huge_deposit()` and `pgtable_trans_huge_withdraw()` maintain per-PMD deposited PTE page tables used when splitting/collapsing transparent huge pages. The generic implementation keeps a FIFO list through the page table page's `lru` list. Callers must hold the PMD lock.

## Deferred PTE Free

If the architecture does not provide `pte_free_defer`, this file implements RCU-deferred freeing:

- `pte_free_defer()` queues a `struct page`'s `rcu_head`.
- `pte_free_now()` releases the page table after the RCU grace period.

This protects lockless page-table walkers from page-table memory disappearing too early.

## Lockless PTE Offset Mapping

The file implements the generic `__pte_offset_map()` family:

- `__pte_offset_map(pmd, addr, pmdvalp)`
- `pte_offset_map_ro_nolock(mm, pmd, addr, ptlp)`
- `pte_offset_map_rw_nolock(mm, pmd, addr, pmdvalp, ptlp)`
- `pte_offset_map_lock(mm, pmd, addr, ptlp)`

`__pte_offset_map()` takes `rcu_read_lock()`, reads the PMD locklessly, rejects none/non-present/THP/bad PMDs, clears bad PMDs, and maps the PTE table. For configurations with split low/high PTE or PMD reads (`CONFIG_GUP_GET_PXX_LOW_HIGH`) and SMP/preempt RCU, it disables interrupts around the lockless PMD read so a TLB flush cannot race between halves.

`pte_offset_map_lock()` retries if the PMD changes after taking the PTE lock, ensuring the returned PTE and spinlock match the same page table.

## Async Kernel Page-Table Free

When `CONFIG_ASYNC_KERNEL_PGTABLE_FREE` is enabled, `pagetable_free_kernel()` queues kernel page-table pages to a global work item. The worker invalidates KVA ranges through `iommu_sva_invalidate_kva_range(PAGE_OFFSET, TLB_FLUSH_ALL)` before freeing queued page tables with `__pagetable_free()`.

## Concurrency and Invariants

- RCU protects page-table pages returned by `pte_offset_map()` style helpers.
- `pte_offset_map_lock()` validates PMD stability after acquiring the page-table lock.
- THP deposit/withdraw require the PMD lock.
- Huge clear/invalidate operations flush the correct hugepage-sized range.
- `free_pgtables()` may free detached page tables without page-table lock; comments warn callers such as khugepaged to avoid these helpers after VMA detachment or `mm_users == 0`.

## Filesystem/MM Relevance

This file is shared page-table infrastructure used by fault handling, GUP, reclaim, migration, THP collapse/split, and mmap teardown. Filesystem-backed mmap behavior depends on these routines for safe PTE lookup, access-bit management, dirty/write-protect transitions, and TLB synchronization.
