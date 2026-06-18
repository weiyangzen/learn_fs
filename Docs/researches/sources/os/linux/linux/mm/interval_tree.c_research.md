# File Research: sources/os/linux/linux/mm/interval_tree.c

Implements interval trees used for reverse mapping of file-backed and anonymous VMAs.

Key pieces:
- Defines `vma_interval_tree` over `struct vm_area_struct` using `shared.rb`, `shared.rb_subtree_last`, `vm_pgoff`, and `vma_last_pgoff()`.
- `vma_interval_tree_insert_after()` inserts a VMA immediately after another VMA with the same start offset, updating augmented subtree-last values.
- Defines anon-vma interval tree wrappers over `struct anon_vma_chain`.
- Public wrappers insert, remove, and iterate anon-vma interval tree nodes.
- Under `CONFIG_DEBUG_VM_RB`, cached start/last offsets are stored and verified.

Purpose:
These trees let the MM quickly find VMAs mapping a file offset range or anonymous folio range, supporting rmap, unmap, migration, reclaim, and memory-failure operations.

Invariant:
`vma_interval_tree_insert_after()` requires identical start pgoff between `node` and `prev`, enforced by `VM_BUG_ON_VMA()`.
