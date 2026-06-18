# File Research: sources/os/linux/linux/mm/userfaultfd.c

This file implements the mm-side mechanics for userfaultfd operations: atomic missing-page fills, zero-page fills, minor-fault continuation, poison markers, write-protection range changes, page-table based page moves, and VMA registration/release.

Major structures and helpers:
- `struct mfill_state` carries userfaultfd context, source/destination ranges, current VMA, current addresses, and current PMD during fill operations.
- `anon_uffd_ops` supplies anonymous-memory userfaultfd behavior: no minor mode, folio allocation through `vma_alloc_folio()` and memcg charging.
- `vma_uffd_ops()` dispatches anonymous VMAs to `anon_uffd_ops`; file-backed VMAs use `vma->vm_ops->uffd_ops`.
- `uffd_mfill_lock()` / `uffd_mfill_unlock()` abstract either per-VMA read locking or mmap read locking.
- `mfill_get_vma()` validates the target range, registered context, mmap-changing state, mode compatibility, hugetlb routing, and availability of VMA-specific uffd operations.
- `mfill_establish_pmd()` allocates and validates the destination PMD/PTE page without overwriting huge/leaf PMDs.

Atomic fill path:
- `mfill_atomic_install_pte()` installs the final PTE for anon or file-cache folios, handles UFFD write-protect markers, rmap setup, mm counters, folio LRU insertion, file-cache unlock, and MMU cache update.
- `mfill_copy_folio_locked()` copies from userspace with page faults disabled while mmap locking is held to avoid recursive mmap-lock deadlocks.
- `mfill_copy_folio_retry()` drops locks, copies with faults enabled, then reacquires and verifies that the VMA still matches saved retry state.
- `__mfill_atomic_pte()` implements COPY and ZEROPAGE folio creation, page-content initialization, filemap insertion, and PTE installation.
- `mfill_atomic_pte_zeropage()` prefers the shared zero page when legal and falls back to a zeroed folio for shared mappings or architectures that forbid zeropage.
- `mfill_atomic_pte_continue()` handles minor-fault continuation by locating an existing file-cache folio with `get_folio_noalloc()`.
- `mfill_atomic_pte_poison()` installs a `PTE_MARKER_POISONED` marker into an empty PTE.
- `mfill_atomic_hugetlb()` is the hugepage-specific path, with alignment checks, hugetlb fault mutex locking, huge PTE allocation, retry after copying outside locks, and explicit unsupported zeropage handling.
- Public wrappers are `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mfill_atomic_continue()`, and `mfill_atomic_poison()`.

Write-protect path:
- `uffd_wp_range()` changes page protections with `MM_CP_UFFD_WP` or `MM_CP_UFFD_WP_RESOLVE`, optionally trying writable upgrades when resolving write-protect.
- `mwriteprotect_range()` validates each VMA in the requested range, handles hugetlb alignment, coordinates with `map_changing_lock`, and invokes `uffd_wp_range()`.

Move path:
- `double_pt_lock()` and `double_pt_unlock()` impose stable ordering for two PTE locks.
- `move_pages_ptes()` handles page-by-page movement for present PTEs, zero-page PTEs, swap PTEs, and migration entries. It uses MMU notifier invalidation, PTE stability checks, PMD stability checks, folio locking, swap-cache validation, and large-folio splitting.
- `move_present_ptes()` can batch contiguous anonymous exclusive order-0 folios when destination PTEs are empty and source folios remain stable.
- `move_swap_pte()` moves exclusive swap entries and updates swap-cache folio rmap/index state if a cached folio exists.
- `move_zeropage_pte()` remaps a zero page to the destination.
- `move_pages()` is the exported userfaultfd move engine. It validates source/destination VMAs, forbids shared/non-anonymous/incompatible mappings, supports THP PMD moves when possible, splits huge PMDs when necessary, and returns either bytes moved or an error.

Registration and release:
- `vma_can_userfault()` checks UFFD mode support, droppable mappings, async WP behavior, PTE marker support, and VMA uffd ops.
- `userfaultfd_set_vm_flags()` updates UFFD flags and recalculates page protections for shared UFFD-WP mappings.
- `userfaultfd_register_range()` modifies VMAs through `vma_modify_flags_uffd()`, verifies MAYWRITE and context consistency, and disables hugetlb PMD sharing when required.
- `userfaultfd_clear_vma()` clears UFFD flags/context and resolves write-protection markers before modifying VMA layout.
- `userfaultfd_release_new()` and `userfaultfd_release_all()` clear contexts from VMAs during context teardown.

Concurrency and correctness themes:
- The file is heavily defensive around VMA replacement, mmap changes, PMD/PTE page disappearance, THP races, swap-cache races, and fatal signals.
- `map_changing_lock` and `ctx->mmap_changing` protect against non-cooperative mapping changes.
- Retry-state comparison checks UFFD flags, VMA type, file identity, inode, and `vm_pgoff` after dropping locks.
- `UFFDIO_MOVE` is intentionally strict: destination must be empty, source holes fail unless explicitly allowed, and incompatible mappings return errors rather than silently degrading.
