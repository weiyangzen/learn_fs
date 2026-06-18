# File Research: sources/os/linux/linux/mm/pagewalk.c

Generic page-table walking framework and folio lookup helper. It drives caller-supplied callbacks over PGD/P4D/PUD/PMD/PTE levels, VMA ranges, kernel page tables, address-space mappings, HugeTLB mappings, and single-address folio walks.

Key responsibilities:
- Implements recursive page-table traversal across all levels with folded-level depth normalization.
- Invokes optional callbacks for PGD, P4D, PUD, PMD, PTE, holes, HugeTLB entries, VMA pre/post hooks, and VMA filtering.
- Supports internal PTE installation through unsafe walker variants while rejecting it from exported safe walkers.
- Splits huge PUD/PMD entries when lower-level handlers require descending into a VMA-backed subtree.
- Handles page-table races by using `ACTION_AGAIN`, `ACTION_CONTINUE`, and `ACTION_SUBTREE`.
- Provides public walkers for `mm` ranges, single VMA ranges, whole VMAs, kernel page tables, debug no-VMA walks, and all VMAs in an address_space interval.
- Implements `folio_walk_start()` to lock the page-table entry for a single address and return the mapped folio, with optional zeropage support.

Important behavior:
- `walk_page_range_mm_unsafe()` performs the core VMA iteration, treating gaps as `pte_hole()` callbacks and honoring `test_walk()`.
- Safe exported walkers call `check_ops_safe()` and reject `install_pte`, reserving page-table population for internal MM code.
- No-VMA walks do not lock PTEs for callbacks and use kernel PTE mapping where appropriate for `init_mm` or kernel addresses.
- `walk_page_mapping()` iterates the mapping interval tree under `i_mmap_rwsem` and clips each VMA to the requested page-index interval.
- `folio_walk_start()` performs a direct page-table descent, locks the relevant PUD/PMD/PTE, records level and entry pointer/value, and requires `folio_walk_end()` by the caller.
- Folio walking deliberately warns against substituting for GUP/pinning and only supports short-term references under the mmap lock.

Dependencies:
- Uses `linux/pagewalk.h`, VMA and mmap locking, hugetlb locking, THP split helpers, architecture TLB/cache hooks, page-table allocation helpers, interval trees, `vm_normal_page*()` helpers, and folio walk structures.

Notable risks:
- Walker callbacks run under caller-specified locking assumptions; incorrect `walk_lock` choice can make VMA/page-table state unstable.
- Hugepage splitting and retry behavior are intentionally conservative to avoid descending through stale or invalid page-table pages.
- Kernel/debug walkers require external synchronization for page tables that can be freed outside normal mmap locking, such as hot-remove-sensitive kernel ranges.
