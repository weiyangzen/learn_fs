# File Research: sources/os/linux/linux/mm/debug_vm_pgtable.c

Late-init self-test for architecture page-table helper semantics. It validates generic expectations documented in `Documentation/mm/arch_pgtable_helpers.rst` against the architecture's PTE/PMD/PUD/P4D/PGD helpers, swap encodings, soft-dirty handling, migration entries, THP entries, HugeTLB entries, and huge-vmap helpers.

Key responsibilities:
- Allocates a synthetic `mm_struct`, VMA, page-table hierarchy, and optional base/huge pages for destructive helper tests.
- Chooses a random user virtual address for tests.
- Finds fixed valid PFNs from usable memory ranges for tests that need present-looking entries without touching memory.
- Constructs swap and migration entries for softleaf/swap helper validation.
- Runs a large set of `WARN_ON()`-based semantic checks at late init.
- Frees allocated pages, page tables, VMA, and mm state after testing.

Test categories:
- PTE basic transforms: same, young/old, dirty/clean, write/write-protect, dirty-write interactions, and no-VMA write helpers.
- PTE advanced operations: `set_pte_at()`, write-protect, get-and-clear, access-flag updates, and test-and-clear-young.
- PMD/PUD THP basic and advanced operations when transparent hugepage support is present.
- PMD/PUD leaf checks for huge entries.
- Huge vmap helpers `pmd_set_huge()`, `pmd_clear_huge()`, `pud_set_huge()`, and `pud_clear_huge()`.
- Upper-level clear/populate helpers for PGD, P4D, PUD, and PMD, accounting for folded levels.
- PTE special and protnone semantics.
- PTE/PMD soft-dirty and swap soft-dirty helpers.
- Swap exclusive helpers and raw swap encode/decode helpers.
- PMD softleaf helpers for THP migration entries.
- Migration swap entry helpers.
- HugeTLB basic dirty/write helpers.
- THP invalidation semantics for PMD and PUD where supported.

Initialization details:
- `init_args()` allocates `mm`, `vma`, P4D/PUD/PMD/PTE tables, initializes fixed PFNs, builds maximum-offset swap entries, and allocates the largest useful page size available for tests.
- `init_fixed_pfns()` scans memblock ranges for PUD-aligned or PMD-aligned usable memory and falls back to the physical address of `start_kernel`.
- `debug_vm_pgtable_alloc_huge_page()` uses contiguous allocation for orders above `MAX_PAGE_ORDER` when available, otherwise uses normal page allocation for supported orders.
- `destroy_args()` frees huge pages, base pages, page-table pages, VMA, and mm state, clearing parent entries first.

Locking and safety:
- Modifying PTE tests use `pte_offset_map_lock()` and unmap/unlock afterward.
- PMD, PUD, and top-level modifying tests take their respective page-table locks.
- Cache flushing is performed after setting entries backed by allocated pages to avoid architecture page-allocation checks seeing stale architecture-specific page flags.
- Some tests skip themselves if required pages could not be allocated or the relevant architecture feature is not enabled.

Execution:
- `debug_vm_pgtable()` is registered with `late_initcall()`.
- Failures are warnings rather than KUnit assertions; this is an init-time architecture compliance diagnostic.
