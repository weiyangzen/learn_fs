# File Research: sources/os/linux/linux/mm/vma.c

This file implements core VMA manipulation for MMU mappings: merge, split, expand, shrink, munmap, mmap region creation, brk growth, unmapped-area search, stack expansion, VMA insertion, dirty-tracking policy, and global lock acquisition.

Core state:
- `struct mmap_state` carries all transient state for `mmap_region()`: target range, file, flags, page protections, descriptor-updated fields, accounting, adjacent VMAs, munmap state, and detached Maple Tree state.
- `MMAP_STATE` initializes mapping state.
- `VMG_MMAP_STATE` translates mmap state into a `vma_merge_struct`.

Merge and split logic:
- `is_mergeable_vma()` checks policy, flags excluding ignored merge flags, file identity, userfaultfd context, and anon name.
- `is_mergeable_anon_vma()` prevents merges that would create problematic anon_vma sharing, especially fork-derived anon_vma chains.
- `can_vma_merge_before()`, `can_vma_merge_after()`, `can_vma_merge_left()`, and `can_vma_merge_right()` enforce adjacency and `vm_pgoff` continuity.
- `vma_prepare()` removes VMAs from file and anon interval trees and takes required locks before structural mutation.
- `vma_complete()` reinserts interval-tree entries, stores newly split VMAs, removes merged-away VMAs, drops references, updates map count, and runs uprobe callbacks.
- `__split_vma()` duplicates a VMA, adjusts endpoints/pgoff, clones policy and anon_vma state, handles file refs and `vm_ops->open`, splits THP/hugetlb state at the boundary, then inserts the new VMA.
- `split_vma()` wraps `__split_vma()` with `sysctl_max_map_count` enforcement.
- `dup_anon_vma()` propagates anon_vma state to an unfaulted merge target when necessary.
- `vma_merge_existing_range()` handles merge opportunities after changing attributes within an existing VMA.
- `vma_merge_new_range()` merges a newly proposed range into adjacent compatible VMAs.
- `vma_merge_copied_range()` adapts merge logic for `mremap()` copy targets.
- `vma_expand()` expands a target VMA and optionally removes the next VMA.
- `vma_shrink()` reduces a VMA from one side and clears the obsolete Maple Tree range.

VMA modification APIs:
- `vma_modify()` first tries merge, then splits leading/trailing ranges as needed.
- `vma_modify_flags()`, `vma_modify_name()`, `vma_modify_policy()`, and `vma_modify_flags_uffd()` specialize `vma_modify()` for flags, anon names, NUMA policy, and userfaultfd context.
- `vma_merge_extend()` expands a VMA by a delta when compatible.

Munmap:
- `vms_gather_munmap_vmas()` splits edge VMAs, checks sealed VMAs, detaches target VMAs into a temporary Maple Tree, accounts pages/locked/accounted/exec/stack/data totals, and prepares userfaultfd unmap notifications.
- `vms_clear_ptes()` and `vms_clean_up_area()` clear page tables and call close hooks as needed.
- `vms_complete_munmap_vmas()` updates map count and mm accounting, optionally downgrades/unlocks mmap lock, removes VMAs, unaccounts memory, validates the mm, and destroys the detached tree.
- `reattach_vmas()` restores detached VMAs on abort before destructive cleanup.
- `vms_abort_munmap_vmas()` either reattaches detached VMAs or completes removal if PTEs/close state already made rollback unsafe.
- `do_vmi_align_munmap()` is the aligned munmap engine.
- `do_vmi_munmap()` validates start/length, finds the first overlapping VMA, and calls the aligned engine.
- `__vm_munmap()` wraps munmap with mmap write locking and userfaultfd completion.

mmap creation:
- `accountable_mapping()` identifies private writable non-hugetlb mappings that need overcommit accounting.
- `__mmap_setup()` prepares overlapping VMA removal, checks expansion limits, handles memory accounting, clears old PTEs, and initializes a descriptor.
- `call_mmap_prepare()` invokes `f_op->mmap_prepare()` before merge attempts and accepts only whitelisted descriptor changes.
- `can_set_ksm_flags_early()` determines whether KSM flags can be applied before callbacks without disrupting mergeability.
- `__mmap_new_file_vma()` attaches file state and invokes legacy `.mmap()` if present, undoing partial driver mappings on failure.
- `__mmap_new_vma()` allocates and inserts a fresh VMA when merge fails.
- `__mmap_complete()` finalizes mmap accounting, perf event, userfaultfd cleanup, mlock state, uprobe mapping, soft-dirty flag, and page protections.
- `__mmap_region()` orchestrates setup, mmap_prepare, KSM updates, merge attempt, new VMA allocation, descriptor fields, completion, and abort cleanup.
- `mmap_region()` is the exported internal entry, enforcing MDWE, architecture flag validation, and writable-file mapping guards.

Other functionality:
- `copy_vma()` creates or merges a target VMA for `mremap()` page-table moves.
- `find_mergeable_anon_vma()` finds adjacent reusable anon_vma state to improve later merging after faults/mprotect.
- `vma_needs_dirty_tracking()` and `vma_wants_writenotify()` decide when shared writable mappings need write fault notification or dirty tracking.
- `mm_take_all_locks()` and `mm_drop_all_locks()` acquire/release all relevant VMA, mapping, hugetlb, and anon_vma locks for operations needing global mm stability.
- `do_brk_flags()` grows or creates the heap/brk VMA with accounting, KSM flags, soft-dirty handling, and merge attempt.
- `unmapped_area()` and `unmapped_area_topdown()` search Maple Tree gaps with alignment and guard-gap constraints.
- `expand_upwards()` and `expand_downwards()` grow stack VMAs with guard-gap, rlimit, mlock, hugepage-only range, overcommit, anon_vma, and Maple Tree updates.
- `insert_vm_struct()` inserts a prebuilt VMA, including anonymous `vm_pgoff` normalization and accounting.
- `vma_mmu_pagesize()` weakly defaults MMU granularity to `vma_kernel_pagesize()`.

Research notes:
- The central design is a two-phase mutation protocol: preallocate Maple Tree changes before modifying VMAs, then alter interval trees, VMA ranges, and mm counters only after rollback boundaries are clear.
- Merge logic preserves sticky flags and avoids removing VMAs with close hooks.
- Munmap intentionally accepts that some rare userfaultfd/split failures can leave VMAs split while reporting an error.
- File-backed VMAs require synchronization with `i_mmap` interval trees and uprobe callbacks; anonymous VMAs require anon_vma interval-tree synchronization.
