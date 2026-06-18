# File Research: sources/os/linux/linux/mm/page_vma_mapped.c

Reverse-mapping helper that finds whether a PFN range is mapped in a specific VMA and returns locked page-table entries for callers that need to inspect or modify them.

Key responsibilities:
- Implements `page_vma_mapped_walk()` for normal, THP, migration, device-private, device-exclusive, and HugeTLB mappings.
- Maps and locks PTE tables, with a stricter synchronous mode for callers that need stronger page-table stability.
- Validates PTE/PMD entries against the target PFN range.
- Handles PMD-mapped THP, PMD migration entries, PTE-mapped THP, and hugepage VMAs.
- Provides `page_mapped_in_vma()` for memory-failure users to find the virtual address of a page mapping.

Important behavior:
- Callers loop until `page_vma_mapped_walk()` returns false; each true return leaves the relevant page-table lock held until `page_vma_mapped_walk_done()`.
- PTE matching supports migration entries only when `PVMW_MIGRATION` is set.
- Device-private and device-exclusive swap-like entries are treated as valid page mappings for reverse-map accounting.
- PMD values are rechecked after locking to detect THP split or concurrent page-table changes.
- Crossing a PMD boundary unmaps the old PTE table, clears state, and sets `PVMW_PGTABLE_CROSSED`.
- HugeTLB walks use `hugetlb_walk()` and `huge_pte_lock()` and expose the huge PTE through `pvmw->pte`.

Dependencies:
- Uses rmap structures, page-table helpers, hugetlb, THP, softleaf swap entry helpers, HMM device memory encodings, VMA address helpers, and memory-failure conditional code.

Notable risks:
- Locking is delicate: callers receive PTE/PMD pointers only while the corresponding page-table lock is held.
- Non-sync PTE mapping intentionally optimizes for the common page-locked case but must retry if the PMD changes under it.
- Range overlap checks avoid overflow and must account for large entries covering more than one base page.
