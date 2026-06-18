# File Research: sources/os/linux/linux/mm/mremap.c

Implementation of `mremap(2)` and internal page-table moving. This file handles shrinking, expanding, moving, fixed-address remapping, `MREMAP_DONTUNMAP`, multi-VMA move-only remaps, userfaultfd notifications, hugetlb alignment, accounting, and efficient page-table relocation.

Key responsibilities:
- Implements `mremap` syscall through `do_mremap()` and a threaded `struct vma_remap_struct`.
- Provides `move_page_tables()` and helpers for moving PTEs, normal PMD/PUD page tables, huge PMDs/PUDs, and hugetlb page tables.
- Handles source/destination VMA copying with `copy_vma()`, page-table movement, VMA ops `mremap`, rollback on move failure, and hugetlb reservation fixup.
- Handles shrink-in-place, expand-in-place, expand-by-moving, fixed-address moving, and multi-VMA fixed move-only remaps.
- Coordinates `MREMAP_DONTUNMAP`, including keeping old VMA metadata, clearing mlock flags, and unlinking old anon_vma chains when appropriate.
- Validates map-count headroom, pgoff overflow, locked-memory limits, `VM_DONTEXPAND`, `VM_PFNMAP`, sealed VMAs, private zero-length duplication, hugetlb alignment, and new address overlap.
- Sends userfaultfd unmap/remap completion or failure notifications after releasing mmap lock.

Important behavior:
- `move_ptes()` copies PTEs under both old and new page-table locks, clears source entries, adjusts architecture PTE state with `move_pte()`, marks soft-dirty, optionally clears uffd-wp state, and flushes old TLB range before releasing locks for present entries.
- Rmap locks are taken when required so reverse-map walkers see either old or new PTEs and do not miss both during moves.
- Page-table move acceleration can move entire PMD/PUD page tables or huge entries when aligned, supported by the architecture, and compatible with userfaultfd state.
- `try_realign_addr()` opportunistically aligns source and destination down to page-table boundaries when safe, increasing chances of moving whole page-table entries.
- `move_page_tables()` wraps movement in cache flush and `MMU_NOTIFY_UNMAP` notifier start/end.
- `prep_move_vma()` checks map-count split headroom, VMA split permissions, and asks KSM to unmerge the source range before moving.
- `copy_vma_and_data()` creates/merges the destination VMA, moves page tables, calls VMA `mremap`, and on failure moves page tables back and sets state so the new mapping is unmapped.
- `unmap_source_vma()` temporarily clears `VM_ACCOUNT` during source unmap to avoid double unaccounting for accountable moves, then restores it on remaining source fragments.
- `mremap_to()` unmaps fixed destination first, shrinks before moving when needed, validates `MREMAP_DONTUNMAP` expansion accounting, picks a destination with `get_unmapped_area()`, then moves.
- `remap_move()` supports batched fixed move-only ranges across multiple VMAs while preserving inter-VMA gaps, but rejects armed userfaultfd VMAs and custom unmapped-area files unless known safe.

Dependencies:
- VMA copy/merge/split/unmap helpers, page-table allocation and lock helpers, architecture PMD/PUD move support, hugetlb/THP movement, rmap locks, KSM, userfaultfd, MMU notifiers, TLB/cache flushing, commit accounting, mlock limits, VMA sealing, and filesystem `get_unmapped_area()` hooks.

Notable risks:
- Page-table moves must preserve visibility to rmap walkers, secondary MMUs, userfaultfd state, and stale TLB invalidation ordering.
- Error recovery is intricate: partial destination VMAs and moved page tables must be reverted or unmapped without corrupting accounting.
- `MREMAP_DONTUNMAP` has unusual semantics: the source VMA remains but page tables move, mlock is cleared, and anon_vma links can be dropped.
- Fixed multi-VMA moves must account for gaps and custom placement hooks; unsafe cases are rejected.
- Sealed VMAs reject all mremap operations with `-EPERM`.
