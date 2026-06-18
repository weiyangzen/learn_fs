# File Research: sources/os/linux/linux/mm/vma.h

This header defines the internal API and state objects for VMA manipulation implemented mostly in `vma.c`, with shared use from mmap, munmap, exec, userfaultfd, and related mm code.

Key structures:
- `struct vma_prepare` describes VMAs/files/anon_vmas involved in a pending structural update, including inserted and removed VMAs.
- `struct unlink_vma_file_batch` batches removal of file-backed VMAs from an address_space interval tree.
- `struct vma_munmap_struct` tracks munmap ranges, neighboring VMAs, userfaultfd list, unlock behavior, accounting totals, and whether PTEs need clearing.
- `enum vma_merge_state` records merge progress/error/success.
- `struct vma_merge_struct` is the central merge descriptor: mm, iterator, prev/middle/next/target VMAs, range, flags, file, anon_vma, policy, userfaultfd context, anon name, copied-from VMA, caller controls, and internal merge-operation flags.
- `struct unmap_desc` describes VMA/page-table ranges for unmapping and page-table freeing.

Important inline helpers and macros:
- `unmap_all_init()` and `unmap_pgtable_init()` initialize `unmap_desc` for broad VMA or page-table removal.
- `UNMAP_STATE` builds an `unmap_desc` around a VMA range and neighbors.
- `VMG_STATE` and `VMG_VMA_STATE` initialize merge descriptors for new ranges or existing VMA modifications.
- `vmg_nomem()` tests for merge OOM state.
- `vma_pgoff_offset()` computes file/page offset for an address inside a VMA.
- `vma_iter_*` helpers wrap Maple Tree iterator operations for preallocation, storage, clearing, loading, gap search, range traversal, rewind, and address/end extraction.
- `compat_set_vma_from_desc()` applies selected `vm_area_desc` fields back to an existing VMA for mmap compatibility paths.
- `is_exec_mapping()`, `is_stack_mapping()`, `is_data_mapping()`, and `is_data_mapping_vma_flags()` classify VMAs for mm accounting.
- `vma_wants_manual_pte_write_upgrade()` identifies VMAs where individual PTE writable upgrades must be handled manually.
- `vm_pgprot_modify()` derives protections from VMA flags.
- `vma_is_sealed()` is enabled only on 64-bit builds.
- `map_deny_write_exec()` enforces MDWE rules by denying writable-executable mappings and executable upgrades from previously non-executable VMAs.

Declared API:
- Structural operations: `vma_expand()`, `vma_shrink()`, `vma_merge_new_range()`, `vma_merge_extend()`, `copy_vma()`, `insert_vm_struct()`.
- Modification helpers: `vma_modify_flags()`, `vma_modify_name()`, `vma_modify_policy()`, `vma_modify_flags_uffd()`.
- Unmap helpers: `do_vmi_align_munmap()`, `do_vmi_munmap()`, `remove_vma()`, `unmap_region()`, `__vm_munmap()`.
- File unlink batching: `unlink_file_vma_batch_init()`, `unlink_file_vma_batch_add()`, `unlink_file_vma_batch_final()`.
- Mapping/search/accounting helpers: `mmap_region()`, `do_brk_flags()`, `unmapped_area()`, `unmapped_area_topdown()`, `find_mergeable_anon_vma()`, `vma_needs_dirty_tracking()`, `vma_wants_writenotify()`.
- Locking helpers: `mm_take_all_locks()`, `mm_drop_all_locks()`.
- Stack growth: `expand_upwards()` when configured, and `expand_downwards()`.
- VMA allocation lifecycle from `vma_init.c`: `vma_state_init()`, `vm_area_alloc()`, `vm_area_dup()`, `vm_area_free()`.
- Exec helpers from `vma_exec.c`: `create_init_stack_vma()` and `relocate_vma_down()`.

Research notes:
- This header is the contract boundary for the VMA subsystem after splitting VMA logic out of larger mm files.
- It encodes assumptions about Maple Tree iterator positioning, mmap write-lock ownership, sticky flags, and caller responsibility for applying modifications after split/merge preparation.
